import { spawnSync } from 'child_process';

import debug0 from 'debug';

const debug = debug0('dev');
const diverImageRecognitionPythonPath = '/home/ubuntu/Image_recogntion/ImageRecognitionTesting.py'
const proposedDiverProfilingPythonPath = '/home/ubuntu/Prediction_Code/Main_Driver_Prediction.py'

/**
 * @param {string}  model_name - current model name, for example: Proposed_LSTM_based
 * @param {string}  source_name - current CSV source file name, for example: Test_Data 
 * @param {string} contentId  - current content id
*/

export function calculateDiverClassByPython(
  model_name: string,
  source_name: string,
  contentId: string,
  
): object {
  try {
    // Calling Python driver class prediction program
    const pythonParams: Array<string> = [
      proposedDiverProfilingPythonPath,
      model_name,
      source_name,
      contentId
    ];
    debug('spawnSync python = ', pythonParams);
    //const { status, stdout, stderr, output } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams);
    const { status, stdout, stderr } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams);

   if (status === 0) {
          //console.log(stdout)
         // console.log(output)
          return JSON.parse(stdout);
    } else {
      console.log(stderr)
      throw stderr.toString();
    }
  } catch (e) {
    throw e;
  }
}

/**
 * @param {string} imagetId  - current image id
 * @param {string}  model_name - current model name, for example: Proposed_LSTM_based
*/

export function diverImageRecognitionByPython(
  imageId: string,
  model_name: string,

): object {
  try {
    // Calling Python driver iamge recognition program
    const pythonParams: Array<string> = [
      diverImageRecognitionPythonPath,
      imageId,
      model_name
    ];
    debug('spawnSync python = ', pythonParams);
    //const { status, stdout, stderr, output } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams);
    const { status, stdout, stderr } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow2_p27/bin/python2.7', pythonParams);
    //const result: object = spawnSync(' /home/ubuntu/anaconda3/envs/tensorflow2_p27/bin/python3.7', pythonParams1);
   if (status === 0) {
          //console.log(stdout)
          //console.log(output)
          return JSON.parse(stdout);
    } else {
      //console.log(stderr)
      //console.log('test')
      throw stderr.toString();
    }
  } catch (e) {
    throw e;
  }
}
