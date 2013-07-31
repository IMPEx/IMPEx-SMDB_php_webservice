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
			       $OutputFiletype, $properties){

  $data2funct = array('function' => 'getDataPointValue',                     // string
		      'filename' => $properties['ProductKey'],               // string
		      'variables' => $variables,                             // list
		      'input_url' => $url_XYZ,
		      'order' => $InterpolationMethod,                       // string: 'linear' || 'nearestgridpoint'
		      'outfmt' => $OutputFiletype);                          // string: 'votable'|| 'netcdf'

// Execute the python script with the JSON data
$result = shell_exec('python impex.py ' . escapeshellarg(json_encode($data2funct))); // TODO: set properly path

// Decode the result  -- ERROR Field? => throw a new error; otherwise keep going well :)
$resultData = json_decode($result, true);

// This will contain: array('fileout' => 'fileout')
var_dump($resultData);
//provide url for that fileout
   // TODO: if out_url exist:   else: throw exception with the errors
  return $resultData['out_url'];
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