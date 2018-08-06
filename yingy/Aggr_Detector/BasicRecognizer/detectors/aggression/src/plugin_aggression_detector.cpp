//plugin_aggression_detector.cpp
//

// Created by yildirim on 03.07.17.

//



#include <detector_status_factory.h>

#include "plugin_aggression_detector.h"

#include <aggression_detector.h>

#include <aggression_detector_motion.h>

#include <aggression_detector_flow_analysis.h>

#include <time.h>

#include <iomanip> //for setfill,setw



using namespace std;

using namespace cv;



basicrecognizerapp::PluginAggressionDetector::PluginAggressionDetector()

        : Plugin(),

          has_preprocessing_step(false),

          prep_crop_h(600),

          prep_crop_w(800),

          prep_scale(1.15f),

          is_audio_enabled(true),

          is_verbose(true),

          detection_interval(60),

          audio_signal(false){

    debug = "debug";

}



basicrecognizerapp::PluginAggressionDetector::~PluginAggressionDetector() {

    if(is_thread_running)

        stop();

}



std::string basicrecognizerapp::PluginAggressionDetector::getStatus() {

    return std::to_string(performance);

}



basicrecognizerapp::DetectorStatus::Ptr basicrecognizerapp::PluginAggressionDetector::getDetectorStatus() {

    return status;

}



bool basicrecognizerapp::PluginAggressionDetector::getThreadStatus() {

    return is_thread_running;

}



void basicrecognizerapp::PluginAggressionDetector::setFrameToStopOn(int frame) {

    this->frame_to_stop = frame;

}



void basicrecognizerapp::PluginAggressionDetector::Thread() {

    cv::VideoCapture cap;

    cap.open(conn.c_str());

    cv::Mat img, result;



    is_thread_running = true;



    speaker->log_info("Aggression detector plugin status: " + std::to_string(is_thread_running));



    int audio_cnt = 0;

    int video_cnt = 0;

    unsigned int cnt = 0;

    //int d = 0;//hy

    //int k = 0;//hy







    while(is_thread_running) {

        cap >> img;



        if (this->has_preprocessing_step) {

            preprocessImg(img, img);

        }



        if (img.empty()) {

            speaker->log_debug("Aggression detector loop ends, cant receive images");

            is_thread_running = false;

            return;

        }



        bool isDetected = detector->detect(img, result);

        //hy interpret final visual detect result

        /*

        if(isDetected){

            d++; //1 2  1 2

            k++; //1 2  3 4

            if(k > 3){

                k = 0;

            }

        }

        else{

            k++; //

        }

        isDetected = false;

        if (d > 1){

            isDetected = true;

            d = 0;

        }

        else{

            isDetected = false;

        }

        */









        if (cnt >= frame_to_stop)

            is_thread_running = false;



        if (cnt % 1 == 0 && has_logger) {

            status->dumpResult(cnt, detectorLog);

            detectorLog.flush();

        }



        if (audio_signal) {

            audio_cnt = detection_interval;

        } else {

            audio_cnt = std::max(audio_cnt - 1, 0);

        }



        if (isDetected) {

            video_cnt = detection_interval;

        }



        if (!is_verbose) {

            img.copyTo(result);

        }



        status->interpretStatusFromBoolean(0, audio_cnt and video_cnt);



        if (audio_cnt > 0 && video_cnt > 0) {

            if (!is_verbose) {

                std::vector <cv::Mat> channels(3);

                cv::split(result, channels);

                channels[0].setTo(0);

                channels[1].setTo(0);

                cv::Rect roi = cv::Rect(0, (result.size().height / 2) - 100, result.size().width, 150);

                channels[0](roi).setTo(255);

                cv::merge(channels, result);

                putText(result, "Aggression", cvPoint((result.size().width / 4), result.size().height / 2),

                        FONT_HERSHEY_COMPLEX_SMALL, 4.0, cvScalar(255, 255, 255), 2, CV_AA);

                //speaker->log_info("Sound Level Exceeded!!!");



            } else {

                putText(result, "Aggression!", cvPoint(100, 100), FONT_HERSHEY_COMPLEX_SMALL, 1.4, cvScalar(0, 0, 255),

                        1, CV_AA);

            }

        }

        audio_signal = false;

        if (!is_audio_enabled)

            audio_signal = true;



        if (fps.isTime()) {

            performance = fps.getFps();

        }



        if (has_preview && cnt % 5 == 0)

            cv::imwrite(preview_folder + "/" + std::to_string(idx) + ".png", result);



        /*

        stringstream filename; //hy

        if (has_preview && cnt % 1 == 0) {//ori 5

            filename << "filename_" << std::setw(6) << std::setfill('0') << cnt << ".png"; //hy

            cv::imwrite(preview_folder + "/" + filename.str(), result); //hy

        }

        */





        cnt++;

        video_cnt = std::max(video_cnt-1, 0);

        speaker->log_debug(std::to_string(audio_signal) + " - " + std::to_string(audio_cnt) + " - " + std::to_string(video_cnt));



        //t0 = clock() - t0;

        //speaker->log_debug("Time elapsed: " + std::to_string(float(t0 / CLOCKS_PER_SEC)));

    }



}



int basicrecognizerapp::PluginAggressionDetector::myMain(std::vector<std::string> cams, std::string detectorcfg) {

    speaker->log_debug("Running the PluginAggressionDetector!");



    if (cams.size() != 1) {

        speaker->log_debug("Expecting exactly one camera in the config!");

        return -1;

    }

    conn = cams[0];



    config.init(detectorcfg.c_str());



    initDetector(config);



    status = DetectorStatusFactory::generateFromString("aggression");



    if(has_logger)

        detectorLog.open(logging_folder + "/aggressionLog.csv", std::ios::out);



    thrdx = new boost::thread(boost::bind(&PluginAggressionDetector::Thread, this));



    return 0;

}



void basicrecognizerapp::PluginAggressionDetector::stop() {

    is_thread_running = false;

    if(!thrdx->try_join_for(boost::chrono::milliseconds(5000)))

        thrdx->interrupt();

    speaker->log_debug("PluginAggressionDetector stopped.");

}



void basicrecognizerapp::PluginAggressionDetector::setMaximalPoints(int max_points) {

    this->maximal_points = max_points;

}



void basicrecognizerapp::PluginAggressionDetector::onEvent(EventType event) {

    speaker->log_info("onEvent called!" + std::to_string(event));

    audio_signal = true;

    if(!is_audio_enabled)

        audio_signal = false;

}



bool basicrecognizerapp::PluginAggressionDetector::initDetector(const ReaderAggressionDetector& config) {

    if (config.isMotionAlgorithm()) {

        speaker->log_info("Starting a motion based aggression detector");

        detector = std::make_shared<icctv::AggressionDetectorMotion>(config, speaker);

    }

    if(config.isFlowAlgorithm()) {

        speaker->log_info("Starting a flow based aggression detector");

        detector = std::make_shared<icctv::AggressionDetectorFlowAnalysis>(config, speaker);

    }

    if(!config.isMotionAlgorithm() && !config.isFlowAlgorithm() ) {

        speaker->log_info("Starting a cascaded detector");

        detector = std::make_shared<icctv::AggressionDetector>(config, speaker);

    }



    this->prep_crop_h = config.getPrepCropH();

    this->prep_crop_w = config.getPrepCropW();

    this->prep_scale = config.getPrepScale();

    this->is_audio_enabled = config.isAudioEnabled();

    this->is_verbose = config.isVerbose();

    this->detection_interval = config.getDetectionInterval();



    if (this->prep_scale > 0.0f and this->prep_crop_w > 0 and this->prep_crop_h > 0)

        this->has_preprocessing_step = true;





    this->speaker->log_info("~~~~~");

    this->speaker->log_info("prep_crop_h: " + std::to_string(prep_crop_h));

    this->speaker->log_info("prep_crop_w: " + std::to_string(prep_crop_w));

    this->speaker->log_info("prep_scale: " + std::to_string(prep_scale));

    this->speaker->log_info("is_audio_enabled: " + std::to_string(is_audio_enabled));

    this->speaker->log_info("is_verbose: " + std::to_string(is_verbose));

    this->speaker->log_info("~~~~~");



    return true;

}



void basicrecognizerapp::PluginAggressionDetector::preprocessImg(const cv::Mat image, cv::Mat& processed_img) {

    image.copyTo(processed_img);

    int framewidth = image.cols;

    int frameheight = image.rows;

    cv::resize(processed_img,

               processed_img,

               cv::Size(int(prep_scale * framewidth),

                        int(prep_scale * frameheight)),

               INTER_CUBIC);

    auto w = processed_img.cols;

    auto h = processed_img.rows;

    auto top_y = h/2 - prep_crop_h/2;

    auto top_x = w/2 - prep_crop_w/2;

    cv::Rect myROI(top_x, top_y, prep_crop_w, prep_crop_h);

    processed_img = processed_img(myROI).clone();

}



extern "C"

{

basicrecognizerapp::Plugin::Ptr construct() {

    return std::make_shared<basicrecognizerapp::PluginAggressionDetector>();

}

}

