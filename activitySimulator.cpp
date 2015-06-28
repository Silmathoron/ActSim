/*
 * ***
 * Activity simulator for ActSim 
 ***********************************/

#include "activitySimulator.hpp"
#include "tools/convertor.hpp"

#include <boost/numeric/ublas/matrix_sparse.hpp>
#include <boost/format.hpp>
#include <math.h>


namespace py = boost::python;


/*
 ***
 * Simulator class
 ************************/

/* *********** *
 * Constructor *
 * *********** */

Simulator::Simulator(csr connectMat, std::map<std::string, var> mapParam) {
	m_connectMat = connectMat;
	m_mapParam = mapParam;
}

Simulator::~Simulator() {}

/* ************** *
 * Set parameters *
 * ************** */

void Simulator::setParam() {
	// load parameters
	for(const auto& iter : m_mapParam) {
		switch (iter.first) {
			case "Threshold": m_rThreshold = iter.second;
			case "IntCst": m_rIntCst = iter.second;
			case "Leak": m_rLeak = iter.second;
			case "Refrac": m_rRefrac = iter.second;
			case "SimulTime": m_rSimulTime = iter.second;
			case "TimeStep": m_rTimeStep = iter.second;
		}
	}
	// compute remaining values
	m_nTotStep = static_cast<int>(floor(m_rSimulTime / m_rTimeStep));
	m_nRefraac = static_cast<int>(floor(m_rRefrac / m_rTimeStep));
}

/* ********** *
 * Simulation *
 * ********** */

/* start */
void Simulator::start() {
	if (!m_bRunning) {
		m_bRunning = true;
		runSimulation();
	}
}

/* running the simulation */
void Simulator::runSimulation() {
	for (int i = 0; i<m_nTotStep; ++i) {
		std::cout << boost::format("Current step: %1%") % i << std::endl;
	}
}

/* ********** *
 * Simulation *
 * ********** */
py::object Simulator::get_results() {
	py::object results;
	return results;
}


/*
 ***
 * Raw constructor (interface with Python)
 ********************************************/

py::object Simulator_init(py::object csrData, py::object xmlParam) {
	// create the convertor and create c++ arguments
	Convertor convertor = Convertor();
	csr connectMat = convertor.makeConnectMat(csrData);
	std::map<std::string, var> mapParam = convertor.convertParam(xmlParam);
	// call the constructor with the converted arguments
	return self.attr("__init__")(connectMat, mapParam);
}


/*
 ***
 * Python module declaration
 ********************************************/

BOOST_PYTHON_MODULE(simulator) {
	// using no_init postpones defining __init__ function until after
	// raw_function for proper overload resolution order, since later
	// defs get higher priority.
	namespace boost::python {
		class_<Simulator>("Simulator", no_init)
			.def("__init__", raw_function(Simulator_init), "simulator")
			.def(init<csr, std::map<std::string, var>>()) // C++ constructor, shadowed by raw ctor
			//.def_readwrite("number", &A::number_)
	}
}
