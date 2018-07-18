//aggression_detector_motion.cpp
//

// Created by yildirim on 11.06.18.

//

#include "aggression_detector_motion.h"

#include <opencv2/imgproc.hpp>

#include <opencv2/video/tracking.hpp>

#include <opencv2/objdetect/objdetect.hpp>

#include <opencv2/highgui/highgui.hpp>



icctv::AggressionDetectorMotion::AggressionDetectorMotion(const ReaderAggressionDetector& config,

                                                          basicrecognizerapp::Speaker::Ptr speaker)

    : split(10),

      history(5),

      aggression_duration_threshold(36),

      need_to_init(true),

      max_points(1000),

      min_distance(20),

      quality_level(0.005),

      target_width(800),

      target_height(600),

      left_b(0),

      right_b(800),

      upper_b(0),

      lower_b(600),

      oflow_winsize(cv::Size(25, 25)),

      max_vector_size(75),

      min_vector_size(5) {

    this->speaker = speaker;



    try {

        this->split = config.getSplit();

        this->history = config.getHistory();

        this->aggression_duration_threshold = config.getDuration();

        this->min_vector_size = config.getMinVecSize();

        this->max_vector_size = config.getMaxVecSize();

        this->oflow_winsize = cv::Size(config.getOflowWinsize(), config.getOflowWinsize());

        this->target_width = config.getPrepCropW();

        this->target_height = config.getPrepCropH();



        this->left_b = config.getLeftBoundary();

        this->right_b = config.getRightBoundary();

        this->upper_b = config.getUpperBoundary();

        this->lower_b = config.getLowerBoundary();



        this->right_b = (this->right_b == -1 ? this->target_width : this->right_b);

        this->lower_b = (this->lower_b == -1 ? this->target_height : this->lower_b);



        logAllParams();



        createBinList(target_width, target_height, this->split, this->split);

        opticalFlow = cv::Mat(target_height, target_width, CV_8UC1, cv::Scalar(0));

    }

    catch (...) {

        throw std::runtime_error("Can't find/read config file!");

    }

}



icctv::AggressionDetectorMotion::~AggressionDetectorMotion() {

    //

}



bool icctv::AggressionDetectorMotion::detect(const cv::Mat& img, cv::Mat& output) {

    cv::GaussianBlur(img, output, cv::Size(5, 5), 0.5, 0.5);

    cv::Mat grayFrames;

    cv::cvtColor(output, grayFrames, CV_BGR2GRAY);

    int framewidth = output.cols;

    int frameheight = output.rows;

    opticalFlow.setTo(cv::Scalar(0));



    cooldown_rate = framewidth / split;

    max_agression_level = cooldown_rate * history;

    counter_threshold = max_agression_level / 4;



    int i,k;

    std::vector<uchar> status;

    std::vector<float> err;



    cv::TermCriteria termcrit(CV_TERMCRIT_ITER | CV_TERMCRIT_EPS, 20, 0.03);



    if (need_to_init) {

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());



        need_to_init = false;

    } else if (!points2.empty()) {

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());



        cv::calcOpticalFlowPyrLK(prev_gray_frame,

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

                line(opticalFlow, points1[i], points2[i], cv::Scalar(255), 1, 1, 0);

                line(output, points1[i], points2[i], cv::Scalar(0, 0, 255), 1, 1, 0);

            } else {

                if (res > this->min_vector_size and res < this->max_vector_size) {

                    line(opticalFlow, points1[i], points2[i], cv::Scalar(255), 1, 1, 0);

                    line(output, points1[i], points2[i], cv::Scalar(0, 0, 255), 1, 1, 0);

                }

            }

            points1[k++] = points1[i];

        }

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());

    }



    updateBinsWithFlow();

    updateBinCounter();

    auto detectionresult = markAggressionBinOnImage(output);

    coolDownBins();



    swap(points2, points1);

    points1.clear();

    grayFrames.copyTo(prev_gray_frame);



    return detectionresult;

}



void icctv::AggressionDetectorMotion::createBinList(int w, int h, int split_x, int split_y) {

    std::vector<Bin> bin_list;

    auto bin_width = w / split_x;

    auto bin_height = h / split_y;



    for (int y = 0; y < split_y; y++) {

        for (int x = 0; x < split_x; x++) {

            auto b = Bin();

            b.top = y * bin_height;

            b.left = x * bin_width;

            b.w = bin_width;

            b.h = bin_height;

            bin_list.push_back(b);

        }

    }

    this->bins = bin_list;

}



void icctv::AggressionDetectorMotion::updateBinsWithFlow(int max_level) {

    for (auto& b : this->bins) {

        cv::Rect roi = cv::Rect(b.left, b.top, b.w, b.h);

        auto local_region = this->opticalFlow(roi);

        auto local_motion = cv::countNonZero(local_region);

        b.level += local_motion;

        b.level = std::min(max_level, b.level);

    }

}



bool icctv::AggressionDetectorMotion::markAggressionBinOnImage(cv::Mat& img) {

    auto is_aggression = false;

    std::vector<cv::Mat> channels(3);

    cv::split(img, channels);



    for (auto& b : this->bins) {

        auto font_channel = 1;

        cv::Rect roi = cv::Rect(b.left, b.top, b.w, b.h);



        auto b_center_x = b.left + (b.w / 2);

        auto b_center_y = b.top + (b.h / 2);

        if (b_center_x < this->left_b or

            b_center_x > this->right_b or

            b_center_y < this->upper_b or

            b_center_y > this->lower_b) {

            continue;

        }



        if (b.counter >= this->aggression_duration_threshold) {

            channels[2](roi).setTo(255);

            is_aggression = true;

        }

        channels[0](roi).setTo(b.level * this->max_agression_level / 255);



        cv::putText(channels[font_channel],

                    std::to_string(b.level) + "/" + std::to_string(b.counter).c_str(),

                    cv::Point(b.left, b.top),

                    cv::FONT_HERSHEY_SIMPLEX,

                    0.5,

                    cv::Scalar(255),

                    1);

    }

    cv::merge(channels, img);

    return is_aggression;

}



void icctv::AggressionDetectorMotion::coolDownBins() {

    for (auto& b : this->bins) {

        b.level -= this->cooldown_rate;

        b.level = std::max(0, b.level);

    }

}



void icctv::AggressionDetectorMotion::updateBinCounter() {

    for (auto& b : this->bins) {

        if (b.level >= this->counter_threshold) {

            b.counter++;

        }

        else

            b.counter = 0;

    }

}



bool icctv::AggressionDetectorMotion::hasPreprocessingStep() {

    return true;

}



void icctv::AggressionDetectorMotion::logAllParams() {

    this->speaker->log_info("~~~~~");

    this->speaker->log_info("max points: " + std::to_string(max_points));

    this->speaker->log_info("min_distance: " + std::to_string(min_distance));

    this->speaker->log_info("min_vector_size: " + std::to_string(min_vector_size));

    this->speaker->log_info("max_vector_size: " + std::to_string(max_vector_size));

    this->speaker->log_info("split: " + std::to_string(split));

    this->speaker->log_info("history: " + std::to_string(history));

    this->speaker->log_info("aggression_duration_threshold: " + std::to_string(aggression_duration_threshold));

    this->speaker->log_info("left_b: " + std::to_string(left_b));

    this->speaker->log_info("right_b: " + std::to_string(right_b));

    this->speaker->log_info("upper_b: " + std::to_string(upper_b));

    this->speaker->log_info("lower_b: " + std::to_string(lower_b));

    this->speaker->log_info("~~~~~");

}

