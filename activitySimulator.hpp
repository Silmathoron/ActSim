#ifndef SIMUL_H
#define SIMUL_H

#include <boost/python.hpp>
#include <boost/variant.hpp>

#include "tools/convertor.hpp"


namespace py = boost::python;

typedef boost::variant<double, std::string, int, bool> var;
typedef std::map<std::string, var>::iterator it_mapParam;



/*
 ***
 * Simulator class
 ***********************/

class Simulator {
	
	public:
		Simulator();
		Simulator(int numNeurons, std::vector<size_t> vecIndPtr, std::vector<int> vecIndices, std::vector<double> vecData, std::map<std::string, var> mapParam);
		~Simulator();
		// set parameters
		void setParam();
		// start simulation
		void start();
		// get results
		py::object get_results();
		
	private:
		Convertor m_convertor;
		// simulation
		void runSimulation();
		// main objects
		std::map<std::string, var> m_mapParam;
		std::vector<size_t> m_vecIndPtr;
		std::vector<int> m_vecIndices;
		std::vector<double> m_vecData;
		// network parameters
		std::vector<double> initPotential();
		std::vector<double> initRestPotential();
		bool m_bRunning;
		int m_nNeurons;
		// the neuron parameters
		double m_rThreshold;
		double m_rLeak;
		double m_rRefrac;
		int m_nRefrac;
		// the simulation parameters
		double m_rSimulTime;
		double m_rTimeStep;
		double m_rSqrtStep;
		int m_nTotStep;
		double m_rNoiseStdDev;
};

#endif
