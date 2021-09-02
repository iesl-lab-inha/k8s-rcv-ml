"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.diverImageRecognitionByPython = exports.calculateDiverClassByPython = void 0;
var child_process_1 = require("child_process");
var debug_1 = require("debug");
var debug = debug_1.default('dev');
var diverImageRecognitionPythonPath = '/home/ubuntu/Image_recogntion/ImageRecognitionTesting.py';
var proposedDiverProfilingPythonPath = '/home/ubuntu/Prediction_Code/Main_Driver_Prediction.py';
/**
 * @param {string}  model_name - current model name, for example: Proposed_LSTM_based
 * @param {string}  source_name - current CSV source file name, for example: Test_Data
 * @param {string} contentId  - current content id
*/
function calculateDiverClassByPython(model_name, source_name, contentId) {
    try {
        // Calling Python driver class prediction program
        var pythonParams = [
            proposedDiverProfilingPythonPath,
            model_name,
            source_name,
            contentId
        ];
        debug('spawnSync python = ', pythonParams);
        //const { status, stdout, stderr, output } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams);
        var _a = child_process_1.spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams), status_1 = _a.status, stdout = _a.stdout, stderr = _a.stderr;
        if (status_1 === 0) {
            //console.log(stdout)
            // console.log(output)
            return JSON.parse(stdout);
        }
        else {
            console.log(stderr);
            throw stderr.toString();
        }
    }
    catch (e) {
        throw e;
    }
}
exports.calculateDiverClassByPython = calculateDiverClassByPython;
/**
 * @param {string} imagetId  - current image id
 * @param {string}  model_name - current model name, for example: Proposed_LSTM_based
*/
function diverImageRecognitionByPython(imageId, model_name) {
    try {
        // Calling Python driver iamge recognition program
        var pythonParams = [
            diverImageRecognitionPythonPath,
            imageId,
            model_name
        ];
        debug('spawnSync python = ', pythonParams);
        //const { status, stdout, stderr, output } = spawnSync('/home/ubuntu/anaconda3/envs/tensorflow_p36/bin/python3.7', pythonParams);
        var _a = child_process_1.spawnSync('/home/ubuntu/anaconda3/envs/tensorflow2_p36/bin/python3.6', pythonParams), status_2 = _a.status, stdout = _a.stdout, stderr = _a.stderr;
        //const result: object = spawnSync(' /home/ubuntu/anaconda3/envs/tensorflow2_p27/bin/python3.7', pythonParams1);
        if (status_2 === 0) {
            //console.log(stdout)
            //console.log(output)
            return JSON.parse(stdout);
        }
        else {
            //console.log(stderr)
            //console.log('test')
            throw stderr.toString();
        }
    }
    catch (e) {
        throw e;
    }
}
exports.diverImageRecognitionByPython = diverImageRecognitionByPython;
