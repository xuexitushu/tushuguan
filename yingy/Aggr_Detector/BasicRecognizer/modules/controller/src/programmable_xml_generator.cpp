//path/BasicRecognizerApp/modules/controller/src
//programmable_xml_generator.cpp
//
//

#include "programmable_xml_generator.h"
#include <iostream>

basicrecognizerapp::ProgrammableXmlGenerator::ProgrammableXmlGenerator()
{
    updateTime();
    tree.put("TrainOccupation.SwVersion", "1.2.3");
    tree.put("TrainOccupation.Train.<xmlattr>.name", "Multimediabahn");
}

#if 0
void basicrecognizerapp::ProgrammableXmlGenerator::visit(DetectorStatusAggression& status, std::string path) {
    updateTime();

    pt::ptree aggression;
    aggression.add("<xmlattr>.Number", number_alarm_indicator++);

    if(status.is_aggression_detected)
        aggression.add("AlarmState","ACTIVE");
    else
        aggression.add("AlarmState","CLEARED");

    tree.add_child("TrainOccupation.Train.AlarmIndicator", aggression);
}

void basicrecognizerapp::ProgrammableXmlGenerator::visit(DetectorStatusSeatOccupancy &status, std::string path) {
    updateTime();

    pt::ptree seat_occupation;
    for(auto st : status.occupancy) {
        pt::ptree seat;
        seat.add("<xmlattr>.Number", number_seat);
        seat.add("<xmlattr>.name", number_seat++);

        if(st.second == DetectorStatusSeatOccupancy::Status::PERSON
           || st.second == DetectorStatusSeatOccupancy::Status::OBJECT_ON_SEAT)
            seat.add("OccupationState", "OCCUPIED");
        else
            seat.add("OccupationState", "FREE");
        seat_occupation.add_child("Seat", seat);
    }

    tree.add_child("TrainOccupation.Train.SeatConfiguration", seat_occupation);

}

void basicrecognizerapp::ProgrammableXmlGenerator::visit(DetectorStatusWheelchairOccupancy &status, std::string path) {
    updateTime();

    pt::ptree wheelchair;
    wheelchair.add("<xmlattr>.Number", number_wheelchair++);

    for(auto st : status.occupancy) {
        if (st.second == DetectorStatusWheelchairOccupancy::Status::EMPTY)
            wheelchair.add("OccupationState", "FREE");
        else if (st.second == DetectorStatusWheelchairOccupancy::Status::REST) {
            wheelchair.add("OccupationState", "OCCUPIED");
            wheelchair.add("OccupationType", "BIKE");
        }
        else if (st.second == DetectorStatusWheelchairOccupancy::Status ::WHEELCHAIR) {
            wheelchair.add("OccupationState", "OCCUPIED");
            wheelchair.add("OccupationType", "WHEELCHAIR");
        }
    }
    tree.add_child("TrainOccupation.Train.MultifunctionArea", wheelchair);
}
#endif

void basicrecognizerapp::ProgrammableXmlGenerator::writeAs(const char* filename) {
    updateTime();
    updateTree();
#if BOOST_VERSION > 106000
    pt::xml_writer_settings<std::string> settings('\t', 1);
#else
    pt::xml_writer_settings<char> settings('\t', 1);
#endif
    pt::write_xml(filename, tree, std::locale(), settings);
}

std::string basicrecognizerapp::ProgrammableXmlGenerator::getAsString() {
    updateTime();
    updateTree();
    std::stringstream ss;
#if BOOST_VERSION > 106000
    pt::xml_writer_settings<std::string> settings('\t', 1);
#else
    pt::xml_writer_settings<char> settings('\t', 1);
#endif
    pt::write_xml(ss, tree, settings);
    return ss.str();
}

void basicrecognizerapp::ProgrammableXmlGenerator::updateTime() {
    time_t t = time(0);
    struct tm * now = std::localtime( & t );
    std::stringstream ss;
    ss << (now->tm_year + 1900) << '-'
       << std::setfill('0') << std::setw(2) << (now->tm_mon + 1) << '-'
       << std::setfill('0') << std::setw(2) <<  now->tm_mday << "T"
       << std::setfill('0') << std::setw(2) << now->tm_hour << ":"
       << std::setfill('0') << std::setw(2) << now->tm_min << ":"
       << std::setfill('0') << std::setw(2) <<now->tm_sec;
    tree.put("TrainOccupation.LastUpdate", ss.str());
}

void basicrecognizerapp::ProgrammableXmlGenerator::updateTree() {
    time_t t = time(0);
    struct tm * now = std::localtime( & t );
    auto min = now->tm_min;
    auto sec = now->tm_sec;

    //Wheelchair
    pt::ptree wheelchair01;
    auto occupied_id = (min % 2)+1;
    wheelchair01.add("<xmlattr>.Number", 3-occupied_id);
    wheelchair01.add("OccupationState", "FREE");

    pt::ptree wheelchair02;
    wheelchair02.add("<xmlattr>.Number", occupied_id);
    wheelchair02.add("OccupationState", "OCCUPIED");
    wheelchair02.add("OccupationType", "WHEELCHAIR");

    tree.add_child("TrainOccupation.Train.MultifunctionArea", wheelchair01);
    tree.add_child("TrainOccupation.Train.MultifunctionArea", wheelchair02);

    //Seat
    pt::ptree seat_occupation;

    pt::ptree seat01;
    seat01.add("<xmlattr>.Number", 1);
    seat01.add("<xmlattr>.name", 1);
    if( (sec > 1 && sec < 15) || (sec > 51 && sec < 60))
        seat01.add("OccupationState", "OCCUPIED");
    else
        seat01.add("OccupationState", "FREE");
    seat_occupation.add_child("Seat", seat01);

    pt::ptree seat02;
    seat02.add("<xmlattr>.Number", 2);
    seat02.add("<xmlattr>.name", 2);
    if( (sec > 11 && sec < 25) || (sec > 51 && sec < 60))
        seat02.add("OccupationState", "OCCUPIED");
    else
        seat02.add("OccupationState", "FREE");
    seat_occupation.add_child("Seat", seat02);

    pt::ptree seat03;
    seat03.add("<xmlattr>.Number", 3);
    seat03.add("<xmlattr>.name", 3);
    if( (sec > 21 && sec < 35) || (sec > 51 && sec < 60))
        seat03.add("OccupationState", "OCCUPIED");
    else
        seat03.add("OccupationState", "FREE");
    seat_occupation.add_child("Seat", seat03);

    pt::ptree seat04;
    seat04.add("<xmlattr>.Number", 4);
    seat04.add("<xmlattr>.name", 4);
    if( (sec > 31 && sec < 40) || (sec > 51 && sec < 60))
        seat04.add("OccupationState", "OCCUPIED");
    else
        seat04.add("OccupationState", "FREE");
    seat_occupation.add_child("Seat", seat04);

    tree.add_child("TrainOccupation.Train.SeatConfiguration", seat_occupation);

    //Aggression
    pt::ptree aggression;
    aggression.add("<xmlattr>.Number", 1);
    if ((sec > 21 && sec < 30) || (sec > 41 && sec < 50))
        aggression.add("AlarmState","ACTIVE");
    else
        aggression.add("AlarmState","CLEARED");
    tree.add_child("TrainOccupation.Train.AlarmIndicator", aggression);

    pt::ptree aggression2;
    aggression2.add("<xmlattr>.Number", 2);
    if ((sec > 31 && sec < 40) || (sec > 51 && sec < 60))
        aggression2.add("AlarmState","ACTIVE");
    else
        aggression2.add("AlarmState","CLEARED");
    tree.add_child("TrainOccupation.Train.AlarmIndicator", aggression2);

    //Wagon
    pt::ptree wagon;
    wagon.add("<xmlattr>.Number", 1);
    if (sec < 41)
        wagon.add("WagonEmptyState", "PERSON");
    else if (sec < 50)
        wagon.add("WagonEmptyState", "NOPERSON_NOOBJECT");
    else
        wagon.add("WagonEmptyState", "PERSON");
    tree.add_child("TrainOccupation.Train.WagonEmptyIndicator", wagon);
}

