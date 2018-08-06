//aggression_detector.cpp
//
// Created by yildirim on 05.07.17.
//

#include "aggression_detector.h"
#include <utils.h>
#include <iostream>

using namespace std;
using namespace cv;

icctv::AggressionDetector::AggressionDetector(const ReaderAggressionDetector& config,
                                              basicrecognizerapp::Speaker::Ptr speaker)
        : need_to_init(true),
          hity(false),
          aggrcounter(0),
          oflow_winsize(cv::Size(31,31)),
          quality_level(0.01),
          min_distance(10),
          haar_scale_factor(2.0),
          haar_min_neighbors(0),
          haar_min_window_size(50),
          haar_max_window_size(50),
          step_size(40),
          min_vector_size(1),
          max_vector_size(1000),
          timer(0) {

    this->speaker = speaker;

    try{
        auto max_points = config.getMaxPoints();
        auto oflow_winsize = config.getOflowWinsize();
        auto quality_level = config.getQualityLevel();
        auto min_distance = config.getMinDistance();
        auto step_size = config.getStepSize();
        auto haar_scale_factor = config.getHaarScaleFactor();
        auto haar_min_neighbor = config.getHaarMinNeighbor();
        auto haar_min_window_size = config.getHaarMinWindowSize();
        auto haar_max_window_size = config.getHaarMaxWindowSize();
        auto min_vector_size = config.getMinVecSize();
        auto max_vector_size = config.getMaxVecSize();

        this->speaker->log_info("~~~~~");
        this->speaker->log_info("max points: " + std::to_string(max_points));
        this->speaker->log_info("oflow_winsize: " + std::to_string(oflow_winsize));
        this->speaker->log_info("quality_level: " + std::to_string(quality_level));
        this->speaker->log_info("min_distance: " + std::to_string(min_distance));
        this->speaker->log_info("step_size: " + std::to_string(step_size));
        this->speaker->log_info("haar_scale_factor: " + std::to_string(haar_scale_factor));
        this->speaker->log_info("haar_min_neighbor: " + std::to_string(haar_min_neighbor));
        this->speaker->log_info("haar_min_window_size: " + std::to_string(haar_min_window_size));
        this->speaker->log_info("haar_max_window_size: " + std::to_string(haar_max_window_size));
        this->speaker->log_info("min_vector_size: " + std::to_string(min_vector_size));
        this->speaker->log_info("max_vector_size: " + std::to_string(max_vector_size));
        this->speaker->log_info("~~~~~");

        setMaxPoints(max_points);
        setOflowWinsize(oflow_winsize);
        setQualityLevel(quality_level);
        setMinDistance(min_distance);
        setStepSize(step_size);
        setHaarScaleFactor(haar_scale_factor);
        setHaarMinNeighbours(haar_min_neighbor);
        setHaarMinWindowsSize(haar_min_window_size);
        setHaarMaxWindowsSize(haar_max_window_size);
        setMinVectorSize(min_vector_size);
        setMaxVectorSize(max_vector_size);
    }
    catch(std::runtime_error err) {
        //speaker->log_error("basicrecognizerapp::PluginAggressionDetector::myMain -> " + std::string(err.what()));
        throw std::runtime_error("Can't find/read config file!");
    }

    if(!loadClassifier(config.getModel().c_str()))
        throw std::runtime_error("Cannot load cascade classifier for aggression detection");
}

bool icctv::AggressionDetector::loadClassifier(const char* path_to_cascade_classifier) {
    if(!path_to_cascade_classifier)
        return false;

    if(!utils::fileExists(path_to_cascade_classifier))
        return false;

    if(!haar_cascade.load(path_to_cascade_classifier))
        return false;
    return true;
}

icctv::AggressionDetector::~AggressionDetector() {

}

bool icctv::AggressionDetector::detect(const cv::Mat& img, cv::Mat& output) {
    bool detectionresult = false;

    img.copyTo(output);
    cv::Mat grayFrames;
    cv::cvtColor(output, grayFrames, CV_BGR2GRAY);
    int framewidth = output.cols;
    int frameheight = output.rows;
    auto opticalFlow = cv::Mat(frameheight, framewidth, CV_8UC3, Scalar(126, 0, 255));
    opticalFlow.setTo(Scalar(0, 0, 0));

    int i,k;
    vector<uchar> status;
    vector<float> err;
    TermCriteria termcrit(CV_TERMCRIT_ITER | CV_TERMCRIT_EPS, 20, 0.03);

    if (need_to_init) {
        goodFeaturesToTrack(grayFrames,
                            points1,
                            max_points,
                            quality_level,
                            min_distance,
                            Mat());

        need_to_init = false;
    } else if (!points2.empty()) {
        goodFeaturesToTrack(grayFrames,
                            points1,
                            max_points,
                            quality_level,
                            min_distance,
                            Mat());

        calcOpticalFlowPyrLK(prev_gray_frame,
                             grayFrames,
                             points2,
                             points1,
                             status,
                             err,
                             oflow_winsize,
                             3,
                             termcrit,
                             0,
                             0.001);

        for (i = k = 0; i < points2.size(); i++) {
            double res = cv::norm(points1[i] - points2[i]);
            if ((points1[i].x - points2[i].x) > 0 and res > this->min_vector_size and res < this->max_vector_size) {
                line(opticalFlow, points1[i], points2[i], Scalar(255, 255, 255), 1, 1, 0);
                line(output, points1[i], points2[i], Scalar(0, 0, 255), 1, 1, 0);
            } else {
                if (res > this->min_vector_size and res < this->max_vector_size) {
                    line(opticalFlow, points1[i], points2[i], Scalar(255, 255, 255), 1, 1, 0);
                    line(output, points1[i], points2[i], Scalar(0, 0, 255), 1, 1, 0);
                }
            }
            points1[k++] = points1[i];
        }
        goodFeaturesToTrack(grayFrames,
                            points1,
                            max_points,
                            quality_level,
                            min_distance,
                            Mat());
    }

    haar_cascade.detectMultiScale(opticalFlow,
                                  hits,
                                  haar_scale_factor,
                                  haar_min_neighbors,
                                  0, // Not used
                                  Size(haar_min_window_size, haar_min_window_size),
                                  Size(haar_max_window_size, haar_max_window_size));

    if (hits.size() > 0) {
        if (aggrcounter < 110) {
            aggrcounter += step_size;
        }
    }
    double percent = 0.6666 * (double) aggrcounter;
    if (aggrcounter <= 110 && aggrcounter > 0) {
        line(output, Point(25, 500), Point(25, 500 - (aggrcounter * 2)), Scalar(245, 206, 52), 15, 2);
        putText(output, to_string((int) percent), cvPoint(40, 500), FONT_HERSHEY_COMPLEX_SMALL, 0.8,
                cvScalar(245, 206, 52), 1, CV_AA);
    } else if (aggrcounter > 105) {
        line(output, Point(25, 500), Point(25, 500 - (aggrcounter * 2)), Scalar(0, 0, 255), 15, 2);
        hity = true;
        putText(output, to_string((int) percent), cvPoint(40, 500), FONT_HERSHEY_COMPLEX_SMALL, 0.8,
                cvScalar(0, 0, 255), 1, CV_AA);
    }
    if (hity && timer < 10) {
        timer = 75;
        hity = false;
    }
    if (timer > 5) {
        timer = timer - 5;
        detectionresult = true;
    }

    if (aggrcounter > 0) {
        aggrcounter -= 2;
    }
    swap(points2, points1);
    points1.clear();
    grayFrames.copyTo(prev_gray_frame);

    return detectionresult;
}

void icctv::AggressionDetector::setDebugMode(std::string debug) {
    this->debug = debug;
}

void icctv::AggressionDetector::setMaxPoints(int points) {
    this->max_points = points;
}

void icctv::AggressionDetector::setOflowWinsize(int win_size) {
    this->oflow_winsize = cv::Size(win_size, win_size);
}

void icctv::AggressionDetector::setQualityLevel(float level) {
    this->quality_level = level;
}

void icctv::AggressionDetector::setMinDistance(int min_distance) {
    this->min_distance = min_distance;
}

void icctv::AggressionDetector::setStepSize(int step_size) {
    this->step_size = step_size;
}

void icctv::AggressionDetector::setHaarScaleFactor(float scale_factor) {
    this->haar_scale_factor = scale_factor;
}

void icctv::AggressionDetector::setHaarMinNeighbours(int min_neighbours) {
    this->haar_min_neighbors = min_neighbours;
}

void icctv::AggressionDetector::setHaarMinWindowsSize(int min_window_size) {
    this->haar_min_window_size = min_window_size;
}

void icctv::AggressionDetector::setHaarMaxWindowsSize(int max_window_size) {
    this->haar_max_window_size = max_window_size;
}

void icctv::AggressionDetector::setMinVectorSize(int min_vector_size) {
    this->min_vector_size = min_vector_size;
}

void icctv::AggressionDetector::setMaxVectorSize(int max_vector_size) {
    this->max_vector_size = max_vector_size;
}

