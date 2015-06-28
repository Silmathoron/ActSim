#ifndef SIMUL_H
#define SIMUL_H

#include <boost/python.hpp>
#include <boost/variant.hpp>


namespace py = boost::python;

typedef boost::variant<double, std::string, int, bool> var;
typedef boost::numeric::ublas::compressed_matrix<double> csr;
typedef std::map<std::string, var>::iterator it_mapParam;



/*
 ***
 * Simulator class
 ***********************/

class Simulator {
	
	public:
		Simulator(csr connectMat, std::map<std::string, var> mapParam);
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
		csr m_connectMat;
		// the neuron parameters
		m_rThreshold;
		m_rIntCst;
		m_rLeak;
		m_rRefrac;
		m_nRefrac;
		// the simulation parameters
		m_rSimulTime;
		m_rTimeStep;
		m_nTotStep;
};

#endif
