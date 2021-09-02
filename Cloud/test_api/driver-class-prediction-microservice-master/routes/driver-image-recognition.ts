//import debug0 from 'debug';
import * as express from 'express';
//import * as moment from 'moment';

import { ERROR } from '../ERROR';
import { diverImageRecognitionByPython } from '../services/SpawnPython';
//import { calculateDiverClassByPython } from '../services/SpawnPython';
//const debug = debug0('dev');

const router = express.Router();

/**
 * @desc POST image information
 * @param id - current imageId
*/ 
router.post('/:id(\\d{0,})', async (req, res) => {
  const id = req.params.id;
  const model_name = "/home/ubuntu/Image_recogntion/mobilenet_0";
  //const model_name = "mobilenet_0";
  //debug(`image_id = ${id}`);
 

  try {
   
    //const p3 = moment();
    //debug('PYTHON started at = ', p3.format('X'));
 
    const result: object = diverImageRecognitionByPython(id, model_name);
                                               
    
    //const p4 = moment();
    //debug('PYTHON finished at = ', p4.format('X'));
    //debug('PYTHON duration = ', p4.diff(p4, 'seconds'));
    //console.log(result)
    res.json(result);
  } catch (e) {
    //debug('ERROR = ', e);
    //console.log(e)
    res.status(ERROR.code500.code).send(e);
  }
});




//const debug = debug0('dev');

/**
 * @desc POST volume information
 * @param id - current contentId
 
router.post('/:id(\\d{0,})', async (req, res) => {
  const id = req.params.id;
  const model_name = "/home/ubuntu/Prediction_Code/Proposed_LSTM_based";
  const source_name = "/home/ubuntu/Prediction_Code/Test_Data";
  //debug(`Prediction_id = ${id}`);
 

  try {
   
    //const p1 = moment();
    //debug('PYTHON started at = ', p1.format('X'));
 
    const result: object = calculateDiverClassByPython(model_name, source_name, id);
                                               
    
    //const p2 = moment();
    //debug('PYTHON finished at = ', p2.format('X'));
    //debug('PYTHON duration = ', p2.diff(p1, 'seconds'));
    //console.log(result)
    res.json(result);
  } catch (e) {
    //debug('ERROR = ', e);
    //console.log(e)
    res.status(ERROR.code500.code).send(e);
  }
});
*/
export default router;
