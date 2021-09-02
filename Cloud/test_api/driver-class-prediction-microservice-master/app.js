"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var bodyParser = require("body-parser");
var cookieParser = require("cookie-parser");
var cors = require("cors");
var express = require("express");
var createError = require("http-errors");
var logger = require("morgan");
var path = require("path");
var compression = require("compression");
var ERROR_1 = require("./ERROR");
var app_config_1 = require("./app_config");
var driver_class_predict_1 = require("./routes/driver-class-predict");
var driver_image_recognition_1 = require("./routes/driver-image-recognition");
var app = express();
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');
app.disable('etag').disable('x-powered-by');
// compress all responses
app.use(compression());
app.use(cors(app_config_1.CORS));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/driver-class-predict', driver_class_predict_1.default);
app.use('/driver-image-recognition', driver_image_recognition_1.default);
// catch 404 and forward to error handler
app.use(function (req, res, next) {
    next(createError(ERROR_1.ERROR.code404.code));
});
// error handler
app.use(function (err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};
    // render the error page
    res.status(err.status || ERROR_1.ERROR.code500.code);
    res.render('error');
});
app.listen(8080, '3.23.18.37');
module.exports = app;
