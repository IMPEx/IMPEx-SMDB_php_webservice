<?php
/**
 * IMPExMethods contains the methods definition of IMPEx using zend framework
 *
 * LICENSE: GPLv3 
 * @package IMPEx_wrapper
 * @copyright Copyright 2013 IMPEx (EC fp7 project)
 * @license http://www.gnu.org/licenses/gpl.html
 */
require('config.php');
require_once('extra_functions.php');
require_once($local_functions[$institute]);


class IMPExMethods {

  /**
   * getDataPointValue returns parameters for a particular model from DataPoints
   *
   * @param String $ResourceID
   * @param String $Variable
   * @param String $url_XYZ
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default Linear )
   * @param String $OutputFiletype (default votable)
   * @return String URL of the parameters requested
   */
  public function getDataPointValue($ResourceID, $Variable = NULL,
				    $url_XYZ, $IMFClockAngle = 0,
				    $InterpolationMethod = 'Linear',
				    $OutputFiletype = 'votable'){
    /*  ==================================================
	Check variables 
	==================================================
    */
    /* ResourceID */
    $model_properties = check_input_ResourceID($ResourceID, $models, $tree_url);
    /* Variable */
    $variables = check_input_Variable($Variable, $model_properties['parameters']);
    /* url_XYZ */   
    check_input_url($url_XYZ);
    /* IMFClockAngle */  
    $IMFClockAngle = check_input_IMFClockAngle($IMFClockAngle);
    /* InterpolationMethod TODO */
    /* OutputFileType  */
    $OutputFileType = check_input_OutputFileType($OutputFileType);

    /* check whether it's a local request or needs to spawn a request to a different smdb ; if local proceed, else soap client?*/
    return true;
  }



  /**
   * getFieldLine returns a magnetic field line/stream lines/etc. lines
   *
   * @param String $ResourceID
   * @param String $Variable
   * @param String $Direction (default forward)
   * @param Float $StepSize (default 100 m) -> needs to be Gridsize/4
   * @param Integer $MaxSteps (default ??)
   * @param Float $StopCondition_Radius (default 0)
   * @param array $StopCondition_Region
   * @param String $OutputFileType (default votable)
   * @param Float $IMFClockAngle (default 0)
   * @param String $url_XYZ
   * @return String URL of the saved output in the format requested
   */
  public function getFieldLine($ResourceID, $Variable = NULL, 
			       $Direction = 'Forward',
			       $StepSize = NULL, 
			       $MaxSteps = NULL, 
			       $StopCondition_Radius = NULL,
			       $StopCondition_Region = NULL, 
			       $OutputFileType = 'votable',
			       $IMFClockAngle = NULL, 
			       $url_XYZ){
    /*  ==================================================
	Check variables 
	==================================================
    */
    /* ResourceID */
    $model_properties = check_input_ResourceID($ResourceID, $models, $tree_url);
    /* Variable TODO*/
    $outVariable = check_input_Variable($Variable, $model_properties['parameters']);    /* Direction */
    if (is_string($Direction)) /* I think SOAP checks this already */
      {
	$Direction = strtolower($Direction);
	if ($Direction == '')
	  {
	    $Direction = 'forward';
	  }
	else if ( $Direction !== 'forward' AND $Direction !== 'backward' )
	  {
	    throw new SoapFault('1', 'Direction needs to be one of '.
				'the possible values [backward or forward]');
	  }
      }
    else if (is_null($Direction))
      {
	$Direction = 'forward';
      }
    else  
      {
	/* Though SOAP will throw the error if it's not a string */
	throw new SoapFault('0', 'Direction needs to be a string');
      }
    /* Stepsize */
    if (is_null($StepSize))
      {
	$StepSize = 100.; /** meters */
      }
    /* if $Stepsize is not a float then SOAP will complain before here */
    /* MaxSteps */
    if (is_null($MaxSteps))
      {
	$MaxSteps = 100; /** steps  This may be end of fieldline?*/
      }
    else if (!is_int($MaxSteps))
      {
	/* SOAP does not complain between integer or float */
	throw new SoapFault('1', 'MaxSteps needs to be an Integer');
      }
    /* StopCondition_Radius */
    if (is_null($StopCondition_Radius))
      {
	$StopCondition_Radius = 0;
      }
    /* StopCondition_Region  */
    if (!is_null($StopCondition_Region))
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
      }
    /* Use defaults? From tree or in the out code?
    else
      {
	
      }
    */
    /* OutputFileType  */
    $OutputFileType = check_input_OutputFileType($OutputFileType);

    /* IMFClockAngle */
    $IMFClockAngle = check_input_IMFClockAngle($IMFClockAngle);

    /* url_XYZ */
    check_input_url($url_XYZ);

    /* RUN external program */
    /* check whether it's a local request or needs to spawn a request to a different smdb ; if local proceed, else soap client?*/
    $url_Param = run_getFieldLine($ResourceID, $Variable, 
				  $Direction,
				  $StepSize,
				  $MaxSteps,
				  $StopCondition_Radius,
				  $StopCondition_Region,
				  $OutputFileType,
				  $IMFClockAngle,
				  $url_XYZ);
    /* TODO: return error message if file not created */
    return url_Param;
  }


}
?>