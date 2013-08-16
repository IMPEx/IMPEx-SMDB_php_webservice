<?php
/**
 * IMPExMethods contains the methods definition of IMPEx using zend framework
 *
 * LICENSE: GPLv3 
 * @package IMPEx_wrapper
 * @copyright Copyright 2013 IMPEx (EC fp7 project)
 * @license http://www.gnu.org/licenses/gpl.html
 *
 *
 *
 * NOTES: I've found that array inputs does not work from python; 
 *        [TypeNotFound: Type not found: '(Array, http://schemas.xmlsoap.org/soap/encoding/, )']
 *        and from Taverna it has not a normal behaviour
 *
 */
require('config.php');
require_once('extra_functions.php');
require_once($local_functions[$institute]);
require_once('complex_types.php');


class IMPExMethods {

  /**
   * getDataPointValue returns parameters for a particular model from DataPoints
   *
   * @param String $ResourceID
   * @param String $Variable
   * @param String $url_XYZ
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default Linear )
   * @param String $OutputFileType (default votable)
   * @return String URL of the parameters requested
   */
  public function getDataPointValue($ResourceID, $Variable = NULL,
				    $url_XYZ, $IMFClockAngle = 0,
				    $InterpolationMethod = 'Linear',
				    $OutputFileType = 'votable'){
    /*  ==================================================
	Check variables 
	==================================================
    */
    /* ResourceID */
    $model_properties = check_input_ResourceID($ResourceID, $GLOBALS['models'], $GLOBALS['tree_url']);

    /* Variable */
    $variables = check_input_Variable($Variable, $model_properties['parameters']);

    /* url_XYZ */   
    check_input_url($url_XYZ);

    /* IMFClockAngle */  
    $IMFClockAngle = check_input_IMFClockAngle($IMFClockAngle);

    /* InterpolationMethod */
    check_input_InterpolationMethod($InterpolationMethod);

    /* OutputFileType  */
    $OutputFileType = check_input_OutputFileType($OutputFileType);

    /* RUN external program */
    /* check whether it's a local request or needs to spawn a request to a different smdb ; if local proceed, else soap client?*/
    $Parameters = array($ResourceID, $variables,
			$url_XYZ, $IMFClockAngle,
			$InterpolationMethod,
			$OutputFileType, $model_properties);
    $url_Param = execute_Method(__FUNCTION__, $model_properties['institute'],
				$Parameters);
    // The method executed throws an error message if file/url is not created
    return $url_Param;
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
   * @param String $StopCondition_Region
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
			       $IMFClockAngle = 0, 
			       $url_XYZ){
    /*  ==================================================
	Check variables 
	==================================================
    */
    /* ResourceID */
    $model_properties = check_input_ResourceID($ResourceID, $GLOBALS['models'], $GLOBALS['tree_url']);

    /* Variable */
    $outVariable = check_input_Variable($Variable, $model_properties['parameters']);

    /* Direction */
    $Direction = check_input_Direction($Direction);

    /* Stepsize */
    $StepSize = check_input_StepSize($StepSize, $model_properties);

    /* MaxSteps */
    $MaxSteps = check_input_MaxSteps($MaxSteps);

    /* StopCondition_Radius */
    $StopCondition_Radius = check_input_StopCondition_Radius($StopCondition_Radius);

    /* StopCondition_Region  */
    $StopCondition_Region = check_input_StopCondition_Region($StopCondition_Region, $model_properties);

    /* OutputFileType  */
    $OutputFileType = check_input_OutputFileType($OutputFileType);

    /* IMFClockAngle */
    $IMFClockAngle = check_input_IMFClockAngle($IMFClockAngle);

    /* url_XYZ */
    check_input_url($url_XYZ);

    /* RUN external program */
    /* check whether it's a local request or needs to spawn a request to a different smdb ; if local proceed, else soap client*/
    $Parameters = array($ResourceID, $Variable, 
			$Direction,
			$StepSize,
			$MaxSteps,
			$StopCondition_Radius,
			$StopCondition_Region,
			$OutputFileType,
			$IMFClockAngle,
			$url_XYZ, $model_properties);

    $url_Param = execute_Method(__FUNCTION__, $model_properties['institute'],
				$Parameters);
    // The method executed throws an error message if file/url is not created
    return $url_Param;
  }

  /**
   * getDataPointValue_spacecraft ...TODO.
   *
   * @param String $ResourceID
   * @param String $Variable
   * @param String $Spacecraft_name
   * @param startDate $StartTime - it should be time input
   * @param String $StopTime
   * @param String $Sampling - (iso8601)
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default linear)
   * @param String $OutputFileType (default votable)
   * @return String URL of the saved output in the format requested
   */
  public function getDataPointValue_spacecraft($ResourceID, $Variable = NULL, 
					       $Spacecraft_name,
					       $StartTime, 
					       $StopTime, 
					       $Sampling,
					       $IMFClockAngle = 0,
					       $InterpolationMethod = 'Linear',
					       $OutputFileType = 'votable'){
    /*  ==================================================
	Check variables 
	==================================================
    */
    return true;
  }

  /**
   * getDataPointSpectra ....TODO
   *
   * @param String $ResourceID
   * @param String $Population
   * @param String $url_XYZ
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default linear)
   * @param String $OutputFileType (default votable)
   * @param String $EnergyChannel
   * @return String URL of the saved output in the format requested
   */
  public function getDataPointSpectra($ResourceID, $Population = NULL, 
				      $url_XYZ,
				      $IMFClockAngle = 0,
				      $InterpolationMethod = 'Linear',
				      $OutputFileType = 'votable',
				      $EnergyChannel = NULL){
    /*  ==================================================
	Check variables 
	==================================================
    */
    return true;
  }

  /**
   * getSurface ...TODO.
   *
   * @param String $ResourceID
   * @param String $Variable
   * @param String $NormalVectorPlane
   * @param String $PlanePoint
   * @param Float $Resolution - default basic grid size -
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default linear)
   * @param String $OutputFileType (default votable)
   * @return String URL of the saved output in the format requested
   */
  public function getSurface($ResourceID, $Variable = NULL, 
			     $NormalVectorPlane,
			     $PlanePoint,
			     $Resolution,
			     $IMFClockAngle = 0,
			     $InterpolationMethod = 'Linear',
			     $OutputFileType = 'votable'){
    /*  ==================================================
	Check variables 
	==================================================
    */
    return true;
  }
  /**
   * getFileURL ...TODO
   *
   * @param String $RunID 
   * @param String $StartTime - it should be time input
   * @param String $StopTime
   * @return String VOtable file! would it work?
   */
  public function getFileURL($RunID, $StartTime,
			     $StopTime){
    /*  ==================================================
	Check variables 
	==================================================
    */
    return true;
  }

  /**
   * getDataPointSpectra_spacecraft ...TODO
   *
   * @param String $ResourceID
   * @param String $Population
   * @param String $Spacecraft_name 
   * @param String $StartTime
   * @param String $StopTime
   * @param String $Sampling
   * @param Float $IMFClockAngle (default 0)
   * @param String $InterpolationMethod (default linear)
   * @param String $OutputFileType (default votable)
   * @return String URL of the saved output in the format requested
   */
  public function getDataPointSpectra_spacecraft($ResourceID,
						 $Population = NULL,
						 $Spacecraft_name,
						 $StartTime,
						 $StopTime,
						 $Sampling,
						 $IMFClockAngle = 0,
						 $InterpolationMethod = 'Linear',
						 $OutputFileType = 'votable'){

     /*  ==================================================
	Check variables 
	==================================================
    */
    return true;
  }

  /**
   * getParticleTrajectory ...TODO
   * 
   * @param String $ResourceID
   * @param String $Direction  (default forward)
   * @param Float $StepSize (default... seconds)
   * @param Int $MaxSteps
   * @param Float $StopCondition_Radius (default 0)
   * @param String $StopCondition_Region
   * @param String $InterpolationMethod (default linear)
   * @param String $OutputFileType (default votable)
   * @param String $url_XYZ
   * @return String URL of the saved output in the format requested
   */
  public function getParticleTrajectory($ResourceID,
					$Direction = 'Forward',
					$StepSize = NULL,
					$MaxSteps = NULL,
					$StopCondition_Radius = NULL,
					$StopCondition_Region = NULL,
					$InterpolationMethod = 'Linear',
					$OutputFileType = 'votable',
					$url_XYZ){

    
    /*  ==================================================
	Check variables 
	==================================================
    */
    /* ResourceID */
    $model_properties = check_input_ResourceID($ResourceID, $GLOBALS['models'], $GLOBALS['tree_url']);

    /* Direction */
    $Direction = check_input_Direction($Direction);

    /* Stepsize */
    $StepSize = check_input_StepSize($StepSize, $model_properties);

    /* MaxSteps */
    $MaxSteps = check_input_MaxSteps($MaxSteps);

    /* StopCondition_Radius */
    $StopCondition_Radius = check_input_StopCondition_Radius($StopCondition_Radius);

    /* StopCondition_Region  */
    $StopCondition_Region = check_input_StopCondition_Region($StopCondition_Region, $model_properties);

    /* InterpolationMethod */
    check_input_InterpolationMethod($InterpolationMethod);

    /* OutputFileType  */
    $OutputFileType = check_input_OutputFileType($OutputFileType);

    /* url_XYZ */
    check_input_url($url_XYZ);

    /* RUN external program */
    /* check whether it's a local request or needs to spawn a request to a different smdb ; if local proceed, else soap client*/
    $Parameters = array($ResourceID, 
			$Direction,
			$StepSize,
			$MaxSteps,
			$StopCondition_Radius,
			$StopCondition_Region,
			$InterpolationMethod,
			$OutputFileType,
			$url_XYZ, $model_properties);

    $url_Param = execute_Method(__FUNCTION__, $model_properties['institute'],
				$Parameters);
    // The method executed throws an error message if file/url is not created
    return $url_Param;
  }
}
?>