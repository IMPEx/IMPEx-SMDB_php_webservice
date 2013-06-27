<?php
/* Functions that spawn the model wrapper */

$dict_functions = array('getDataPointValue' => 'run_getDataPointValue',
			'getFieldLine' => 'run_getFieldLine',
			'getDataPointValue_spacecraft' => 'run_getDataPointValue_spacecraft',
			'getDataPointSpectra' => 'run_getDataPointSpectra',
			'getSurface' => 'run_getSurface',
			'getFileURL' => 'run_getFileURL',
			'getDataPointSpectra_spacecraft' => 'run_getDataPointSpectra_spacecraft',
			'getParticleTrajectory' => 'run_getParticleTrajectory');




/**
 *
 */
function run_getDataPointValue($ResourceID, $variables,
			       $url_XYZ, $IMFClockAngle,
			       $InterpolationMethod,
			       $OutputFiletype){
  return true;
}



/**
 *
 */
function run_getFieldLine($ResourceID, $Variable, 
			  $Direction, $StepSize,
			  $MaxSteps, $StopCondition_Radius,
			  $StopCondition_Region, $OutputFileType,
			  $IMFClockAngle, $url_XYZ){


  /* ssh $ex_server 'wget ... $path/file' */
  /* ssh $ex_server 'python... ' */
  /* scp $ex_server:$path/$file /outpath/ */
  return true;
}

?>