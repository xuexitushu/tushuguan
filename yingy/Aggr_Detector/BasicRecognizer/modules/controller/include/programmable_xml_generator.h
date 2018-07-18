//programmable_xml_generator.h
//
//

#ifndef ICCTV_RECOGNIZER_PROGRAMMABLEXMLGENERATOR_H
#define ICCTV_RECOGNIZER_PROGRAMMABLEXMLGENERATOR_H

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/foreach.hpp>

#include <plugin_result_writer.h>
#include <detector_status_aggression.h>

namespace pt = boost::property_tree;

namespace basicrecognizerapp {
    class PluginResultWriter;

    class ProgrammableXmlGenerator : public PluginResultWriter {
    public:

        ProgrammableXmlGenerator();

        void writeAs(const char* filename);

        std::string getAsString();

    private:
        pt::ptree tree;
        void updateTime();
        void updateTree();
    };
}


#endif //ICCTV_RECOGNIZER_PROGRAMMABLEXMLGENERATOR_H

