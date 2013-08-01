<?php
/**
 * extra_functions contains a list of helpful functions used by IMPEx
 *
 * LICENSE: GPLv3 
 * @package IMPEx_wrapper
 * @copyright Copyright 2013 IMPEx (EC fp7 project)
 * @license http://www.gnu.org/licenses/gpl.html
 */


/**
 * is_numeric_array checks whether all elements are numeric
 * @param array $array 
 * @return bool 
 */
function is_numeric_array($array){
  foreach ($array as $elem)
    {
      if (!is_numeric($elem))
	return false;      
    }
  return true;
}

/**
 * url_exists checks whether an url works
 * @param string $url
 * @return bool 
 */
function url_exists($url){
  $check = @fopen($url, 'r');
  if ($check)
    {
      return true;
    }
  return false;
}

/*  Should the tree.xml reader go as a class */

/**
 * check_resourceID finds out whether the ResourceID input it exists
 * @param string $ResourceID
 * @param string $tree_url
 * @return bool
 */
function check_resourceID($ResourceID, $tree_url){
  $treexml = file_get_contents($tree_url);
  $runs = new SimpleXmlElement($treexml);
  foreach ($runs->NumericalOutput as $entry)
    {
      if ($entry->ResourceID == $ResourceID) 
	{
	  return true;
	}
    }
  return false;
}

/**
 * find_resourceID locate which tree.xml has to been search
 * @param string $ResourceID
 * @param array $ResourceDict
 * @param string - modelLocation
 */
function find_resourceID($ResourceID, $resourceList){
  foreach ($resourceList as $key => $value)
    {  
      if (preg_match("/".$value."/", $ResourceID))
	{
	  return $key;
	}
    }
  return NULL;
}

/**
 * execute_ExternalMethod
 * @param String $Server
 * @param String $MethodName
 * @param Array $Parameters
 * @return String URL with the results
 */
function execute_ExternalMethod($Server, $MethodName, array $Parameters){

  $client = new Zend_Soap_Client($Server);
  $result = call_user_func_array(array($client,$MethodName),
				 $Parameters);

  return $result;
}

/**
 * execute_InternalMethod
 * @param String $MethodName
 * @param Array $Parameters
 * @return String URL with the results
 */
function execute_InternalMethod($MethodName, array $Parameters){
  /* Function to execute */
  $local_Method = $GLOBALS['dict_functions'][$MethodName];
  $result = call_user_func_array($local_Method, $Parameters);
}
/*
   =========================================================
   SOAP methods check functions
   =========================================================
*/

/**
 * check_input_ResourceID finds whether the resourceID exist and extract the properties needed
 * @param string $ResourceID
 * @param array $resourceList gives an array with the models and their names
 * @param array $tree_url provides where the tree.xml of each smdb is
 * @return array $resource_properties with a list of properties of such resourceID
 * @throws SoapFault for (1) an empty ID, (2) not an accessible model, (3) not a real ID
 */
function check_input_ResourceID($ResourceID, $resourceList, $tree_url){
  if (is_null($ResourceID) or $ResourceID == '')
    {
      throw new SoapFault('1', 'Input ResourceID is needed.');
    }
  $model_institute = find_resourceID($ResourceID, $resourceList);
  if (is_null($model_institute))
    {
      throw new SoapFault('2', 'The ResourceID is not from a model accessible from here');
    }
  if (!check_resourceID($ResourceID, $tree_url[$model_institute]))
    {
      throw new SoapFault('3', 'The ResourceID does not exist in this SMDB');
    }
  $tree = file_get_contents($tree_url[$model_institute]); /*TODO: caught exeption instead of above if?*/
  $model = new SimpleXmlElement($tree);
  foreach ($model->NumericalOutput as $entry)
    {
      if ($entry->ResourceID == $ResourceID)
	{
	  try {
	    $productkey = (string)$entry->AccessInformation->AccessURL->ProductKey; // used as filename in FMI -TODO: same for the rest?
	  } catch (Exception $e) {
	    $productkey = '';
	  }
	  $parameters = array();
	  foreach ($entry->Parameter as $param)
	    {
	      array_push($parameters, $param->ParameterKey);
	    }
	  $resourceIDSimulation = $entry->InputResourceID;
	  foreach ($model->SimulationRun as $simulation)
	    {
	      if ($simulation->ResourceID == $resourceIDSimulation)
		{
		  $gridstructure = $simulation->SimulationDomain->GridStructure;
		  $gridcellsize  = preg_split("/[\s,]+/",
					      $simulation->SimulationDomain->GridCellSize);
		  $coordinates_order = preg_split("/[\s,]+/",
						  $simulation->SimulationDomain->CoordinatesLabel);
		  $valid_min = preg_split("/[\s,]+/",
					  $simulation->SimulationDomain->ValidMin);
		  $valid_max =  preg_split("/[\s,]+/",
					  $simulation->simulationdomain->ValidMax);
		}
	    }
	    
	  
	}
    }
  // TODO: this produces some notices in logs because the vars are not defined outside the loop
  $resource_properties = array('resourceID' => $ResourceID,
			       'institute' => $model_institute,
			       'parameters' => $parameters,
			       'resourceIDSimulation' => $resourceIDSimulation,
			       'gridStructure' => $gridstructure,
			       'gridSize' => $gridcellsize,
			       'coordinates' => $coordinates_order,
			       'valid_min' => $valid_min,
			       'valid_max' => $valid_max,
			       'ProductKey' => $productkey);
  return $resource_properties;
}

/**
 * check_input_Variable identifies whether the variables asked exist
 * @param string $Variable which default is NULL
 * @param array $parameters is the list of possible values to extract
 * @return array with the valid list of parameters 
 * @throws SoapFault for (1) a wrong variable
 */
function check_input_Variable($Variable, array $parameters){
  if (is_null($Variable) or $Variable == '')
    {
      return $parameters;
    }
  else
    {
      $outVariable = array();
      foreach (preg_split("/[\s(,|;)]+/", $Variable) as $var_requested)
	{
	  if (in_array($var_requested, $parameters))
	    {
	      array_push($outVariable, $var_requested);
	    }
	  else
	    {
	      throw new SoapFault('1', 'The variable requested: '.$var_requested.
				  ' is not available in the model requested.');
	    }
	}
    }
  return $outVariable;

}

/**
 * check_input_url finds whether the input_url is valid 
 * @param string $input_url
 * @throws SoapFault for (1) an empty url or (2) not accessible
 */
function check_input_url($input_url){
  if (is_null($input_url) or $input_url == '')
    {
      throw new SoapFault('1', 'Input url with x,y,z coordinates is needed '.
			  'for this method.');
    }
  else if (!url_exists($input_url))
    {
      throw new SoapFault('2', 'The URL input ' . $input_url . ' cannot be accessed.');
    }
}

/**
 * check_input_url finds whether the input_url is valid 
 * @param float $input_IMFCAngle
 * @return float $input_IMFCAngle
 */
function check_input_IMFClockAngle($input_IMFCAngle){
  if (is_null($input_IMFCAngle))
    {
      $input_IMFCAngle = 0;
    }
  /* any conditions to add to IMFClockAngle? (value range?) */
  return $input_IMFCAngle;
}

/**
 * check_input_InterpolationMethod
 * @param string $InterpolationMethod
 * @return string $input_InterpolationMethod (default linear)
 * @throws
 */
function check_input_InterpolationMethod($input_InterpolationMethod){
  if (is_null($input_InterpolationMethod) or $input_InterpolationMethod == '')
    {
      return 'linear';
    }
  else
    {
      $input_InterpolationMethod = strtolower($input_InterpolationMethod);
      /* this should be done in a more general way where we have a list of possible
	 methods and check wether the input correspond to any of those */
      if ($input_InterpolationMethod !== 'linear' AND $InterpolationMethod !== 'nearestgridpoint')
	{
	  throw new SoapFault('1', 'InterpolationMethod needs to be one of '.
			      'the possible values [Linear or NearestGridPoint]');
	}
    }
}

/**
 * check_input_OutputFileType finds whether the input_OutputFileType is valid 
 * @param string $input_OutputFileType
 * @return string $input_OutputFileType (default votable)
 * @throws SoapFault for a (1) not supported output
 */
function check_input_OutputFileType($input_OutputFileType){
  if (is_null($input_OutputFileType) or $input_OutputFileType == '')
    {
      $input_OutputFileType = 'votable';
    }
  else
    {
      $input_OutputFileType = strtolower($input_OutputFileType);
      if ($input_OutputFileType !== 'votable' AND $input_OutputFileType !== 'netcdf')
	{
	  throw new SoapFault('1', 'OutputFileType needs to be one of '.
			      'the possible values [votable or netcdf]');
	}
    }
  return $input_OutputFileType;
}

/**
 * check_input_Direction tests the input value
 * @param string Direction 
 * @return string Direction (default forward)
 * @throw SoapFault for (1) a non supported input
 */
function check_input_Direction($Direction){
  if (is_null($Direction) OR ($Direction == ''))
    {
      return 'forward';
    }
  else 
    {
      $Direction = strtolower($Direction);
      if ( $Direction !== 'forward' AND $Direction !== 'backward' )
	{
	  throw new SoapFault('1', 'Direction needs to be one of '.
			      'the possible values [backward or forward]');
	}
    }
}

/**
 * check_input_StepSize finds out whether the input is valid or asign the default value depending on the model
 * @param float $StepSize
 * @param array $model_properties with the keys: gridStructure and gridSize
 * @return float $StepSize
 * @throw SoapFault if (1) StepSize is not greater than 0, (2) keys are not present in the model_properties
 */
function check_input_StepSize($StepSize, array $model_properties){
  if (is_null($StepSize))
    {
      if (array_key_exists('gridStructure', $model_properties) AND 
	  array_key_exists('gridSize', $model_properties))
	{
	  $min_gridSize = min($model_properties['gridSize']);
	  if (preg_match("/constant/", strtolower($model_properties['gridStructure'])))
	    {
	      return $min_gridSize/4.;
	    }
	  else if (preg_match("/variable/", strtolower($model_properties['gridStructure']))) /* when is not constant */
	    {
	      /* assuming that it follows something like: "Variable. 3 levels..."
		 or the first number in that string is the number of levels. */
	      preg_match_all('/\d+/', $model_properties['gridStructure'],  $smaller_level);

	      /*TODO: This may fail if there's not a number on the gridStructure! */

	      /* it's divided by 2^(levels-1) to know the smaller grid size,
		 and then divided by 4 as the deffault stepsize */
	      return $min_gridSize/pow(2,$smaller_level - 1)/4.;
	    }
	  else
	    {
	      /*model grid not supported*/
	      throw new SoapFault('2', 'the GridStructure is not Constant or Variable');
	    }
	}
      else
	{
	  throw new SoapFault('2', 'there is some problem with the model description');
	}
    }
  else if  ($StepSize <= 0)
    {
      throw new SoapFault('1', 'The StepSize needs to be greater than 0');
    }
  else
    {
      return $StepSize;
    }
}

/**
 * check_input_MaxStep
 * @param int $MaxStep
 * @return ??
 * @throw SoapFault if number is not integer
 */
function check_input_MaxSteps($MaxSteps){
  if (is_null($MaxSteps))
    {
      return 100; /* steps; or maybe Null so it goes till the end?  */
    }
  else if (!is_int($MaxSteps))
    {
      /* SOAP does not complain between integer or float */
      throw new SoapFault('1', 'MaxSteps needs to be an Integer');
    }
}

/**
 * check_input_StopCondition_Radius
 * @param float StopCondition_Radius
 * @return float StopCondition_Radius (default 0)
 * @throw SoapFault if (1) input < 0
 */
function check_input_StopCondition_Radius($StopCondition_Radius){
  if (is_null($StopCondition_Radius))
    {
      $StopCondition_Radius = 0;
    }
  else if ($StopCondition_Radius < 0)
    {
      throw new SoapFault('1', 'StopCondition_Radius need to be larger than 0');
    }
  return $StopCondition_Radius;	      
}

/**
 * check_input_StopCondition_Region
 * @param string StopCondition_Region - a six element separated by " ","," or ";"
 * @param array $model_properties with the keys: 'valid_min' and 'valid_max'
 * @return array $StopCondition_Region as an array (or NULL)
 * @throw SoapFault if (1) wrong format, (2) Out of boundaries, (3) Model boundaries not in model_properties
 */
function check_input_StopCondition_Region($StopCondition_Region, array $model_properties){
  if (!is_null($StopCondition_Radius))
    {
      $StopCondition_Region_array = preg_split("/[\s(,|;)]+/", $StopCondition_Region);
      if (count($StopCondition_Region_array) !== 6)
	{
	  throw new SoapFault('1', 'StopCondition_Region needs 6 elements '.
			      'separated by "," or ";". The region input has '.
			      count($StopCondition_Region_array).' elements.');
	}
      else if (!is_numeric_array($array))
	{
	  throw new SoapFault('1', 'StopCondition_Region needs 6 float elements');
	}
      $StopCondition_Region = $StopCondition_Region_array; /* so we can return NULL */
      if (array_key_exists('valid_min', $model_properties) AND
	  array_key_exists('valid_max', $model_properties))
	{
	  /* compare input array with model boundaries */
	  $lower_boundaries = array($StopCondition_Radius[0], $StopCondition_Radius[2], $StopCondition_Radius[4]);
	  $upper_boundaries = array($StopCondition_Radius[1], $StopCondition_Radius[3], $StopCondition_Radius[5]);
	  if ($lower_boundaries < $model_properties('valid_min'))
	    {
	      throw new SoapFault('2', 'The lower boundaries (x,y,z) = ['.
				  implode(",", $lower_boundaries).
				  '] are outside model boundaries ['.
				  implode(",", $model_properties['valid_min']).
				  ']');
	    }
	  else if ( $upper_boundaries >  $model_properties('valid_max'))
	    {
	      throw new SoapFault('2', 'The upper boundaries (x,y,z) = ['.
				  implode(",", $upper_boundaries).
				  '] are outside model boundaries ['.
				  implode(",",$model_properties['valid_max']).
				  ']');
	    }
	}
      else
	{
	  /* model coordinates not in array! */
	  throw new SoapFault('3', 'the model boundaries are not available');
	}
    }
  /* if NULL return null or valid_min and valid_max? */
  return $StopCondition_Region;
}

/*
   =========================================================
   Execute methods
   =========================================================
*/

/**
 * execute_ExternalMethods calls the apropriate function to execute
 *
 * @param String $MethodName 
 * @param String $institute
 * @param Array $Parameters list of arguments of each method/function
 * @return String $url_Param with the place where to find the result
 */
function execute_Method($MethodName, $institute, array $Parameters){

    if ($GLOBALS['institute'] !== $institute)
      {
	$url_Param = execute_ExternalMethod($GLOBALS['servers'][$institute],
					    $MethodName,
					    $Parameters);
      }
    else
      {
	$url_Param = execute_InternalMethod($MethodName, $Parameters);
      }

    return $url_Param;
}



?>