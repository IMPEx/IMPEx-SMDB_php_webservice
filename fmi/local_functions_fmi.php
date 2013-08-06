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
function run_fmi_any($data){
  // Execute the python script with the JSON data
  // python with "-W ignore" flag to ignore the warning messages that are send to stdout and we then cannot read as json
  // Though it would be nice to report these errors/warnings to the user in any way...
  $result = shell_exec('python -W ignore fmi/code/impex.py ' . escapeshellarg(json_encode($data))); 

  // Decode the result  
  $resultData = json_decode($result, true);
  //- ERROR Field? => throw a new error; otherwise keep going well :)
  if ($resultData['error'] != '')
    {
      throw new SoapFault('1', 'Something wrong with the input variables, check: '.$resultData['error']);
    }
  
  //provide url for that fileout
  else return $resultData['out_url'];
}



/**
 * run_getDataPointValue executes the local too in FMI (hcintpol) for the
 *  requested variable and points (as a votable) for the ResourceID.
 * @param string $ResourceID
 * @param array $variables
 * @param string $url_XYZ
 * @param float $IMFClockAngle
 * @param string $InterpolationMethod
 * @param string $OutputFiletype
 * @param array $properties
 * @throws SoapFault for (1) if there's some error while executing hcintpol 
 *         (e.g. if not variable is returned)
 */
function run_getDataPointValue($ResourceID, $variables,
			       $url_XYZ, $IMFClockAngle,
			       $InterpolationMethod,
			       $OutputFiletype, $properties){

  $data2funct = array('function' => 'getDataPointValue',                     // string
		      'filename' => $properties['ProductKey'],               // string  TODO: FIXME! it produces a list {'0':'file...'} ????
		      'variables' => $variables,                             // list
		      'url_XYZ' => $url_XYZ,
		      // 'IMFClockAngle' => $IMFClockAngle,                     // float
		      'order' => $InterpolationMethod,                       // string: 'linear' || 'nearestgridpoint'
		      'OutputFiletype' => $OutputFiletype);                          // string: 'votable'|| 'netcdf'


  return run_fmi_any($data2funct);
}



/**
 *
 */
function run_getFieldLine($ResourceID, $Variable, 
			  $Direction, $StepSize,
			  $MaxSteps, $StopCondition_Radius,
			  $StopCondition_Region, $OutputFileType,
			  $IMFClockAngle, $url_XYZ, $properties){


  $data2funct = array('function' => 'getFieldLine',                          // string
		      'filename' => $properties['ProductKey'],
		      'variables' => $variables,                             // list
		      'direction' => $Direction,                             // string: 'backward' || 'forward'
		      'stepsize' => $StepSize,                               // float
                      'maxsteps' => $MaxSteps,                               // integer
		      'stop_radius' => $StopCondition_Radius,                // float
		      'stop_box' => $StopCondition_Region,                   // ??
		      'url_XYZ' => $url_XYZ,
		      // 'IMFClockAngle' => $IMFClockAngle,                     // float
		      'OutputFiletype' => $OutputFiletype);                  // string: 'votable'|| 'netcdf'

  return run_fmi_any($data2funct);
}

?>