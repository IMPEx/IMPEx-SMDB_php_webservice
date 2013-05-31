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
      if (preg_match("/$value/", $ResourceID))
	{
	  return $key;
	}
    }
  return NULL;
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
  if (!check_resourceID($ResourceID, $tree_url))
    {
      throw new SoapFault('3', 'The ResourceID does not exist in this SMDB');
    }
  $tree = file_get_contents($tree_url[$model_institute]);
  $model = new SimpleXmlElement($tree);
  foreach ($model->NumericalOutput as $entry)
    {
      if ($entry->ResourceID == $ResourceID)
	{
	  $parameters = array();
	  foreach ($entry->parameter->parameterkey as $param)
	    {
	      array_push($parameters, $param);
	    }
	  $resourceIDSimulation = $entry->inputresourceid;
	  foreach ($model->simulationrun as $simulation)
	    {
	      if ($simulation->resourceid == $resourceIDSimulation)
		{
		  $gridstructure = $simulation->simulationdomain->gridstructure;
		  $gridcellsize  = preg_split("/[\s,]+/",
					      $simulation->simulationdomain->gridcellsize);
		}
	    }
	    
	  
	}
    }
  
  $resource_properties = array('resourceID' => $ResourceID,
			       'institute' => $model_institute,
			       'parameters' => $parameters,
			       'resourceIDSimulation' => $resourceIDSimulation,
			       'gridStructure' => $gridstructure,
			       'gridSize' => $gridcellsize);
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



?>