/*
 * ***
 * Activity simulator for ActSim 
 ***********************************/

#include "activitySimulator.hpp"
#include "tools/convertor.hpp"

#include <boost/numeric/ublas/matrix_sparse.hpp>
#include <boost/format.hpp>
#include <math.h>

#include "viennacl/vector.hpp"
#include "viennacl/compressed_matrix.hpp"


namespace py = boost::python;
namespace ublas = boost::numeric::ublas


/*
 ***
 * Simulator class
 ************************/

/* *********** *
 * Constructor *
 * *********** */

Simulator::Simulator(csr connectMat, std::map<std::string, var> mapParam) : m_matConnect(connectMat), m_mapParam(mapParam)
{
	m_nNeurons = m_matConnect.size1();
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
	// create on the GPU
	viennacl::vector<double> d_vecPotential(m_nNeurons);
	viennacl::vector<double> d_vecNoise(m_nNeurons);
	viennacl::vector<double> d_vecThreshold(m_nNeurons);
	viennacl::vector<int> d_vecActive(m_nNeurons);
	viennacl::vector<int> d_vecRefractory(m_nNeurons);
	viennacl::compressed_matrix<double> d_matConnect(m_nNeurons, m_nNeurons);
	viennacl::compressed_matrix<double> d_matActionPotentials(m_nNeurons, m_nNeurons);
	// initialize GPU from ublas
	initDeviceContainers(d_vecPotential, d_vecNoise, d_vecThreshold,
		d_vecActive, d_vecRefractory, d_matConnect,	d_matActionPotentials);
	// run
	for (int i = 0; i<m_nTotStep; ++i) {
		std::cout << boost::format("Current step: %1%") % i << std::endl;
	}
}

/* Send the results to DataProcessor */

py::object Simulator::get_results() {
	py::object results;
	return results;
}

/* Initialize GPU containers */

void Simulator::initDeviceContainers( d_vecPotential, d_vecNoise, d_vecThreshold,
	d_vecActive, d_vecRefractory, d_matConnect, d_matActionPotentials)
{
	// create the required items on the CPU
	ublas::zero_vector<int> vecZero(m_nNeurons);
	ublas::vector<double> vecPotential(m_nNeurons);
	vecPotential = initPotential();
	// copy onto device
	viennacl::copy(vecPotential, d_vecPotential);
	viennacl::copy(vecZero, d_vecRefractory);
	viennacl::copy(vecZero, d_vecActive);
	viennacl::copy(m_matConnect, d_matConnect);
}

/* Initialize the potentials */

ublas::vector<double> Simulator::initPotential() {
	ublas::vector<double> vecPotential(m_nNeurons);
	return vecPotential;
}


/*
 ***
 * Raw constructor (interface with Python)
 ********************************************/

py::object Simulator_init(py::object csrData, py::object xmlParam) {
	// create the convertor and create c++ arguments
	Convertor convertor = Convertor();
	csr matConnect = convertor.makeConnectMat(csrData);
	std::map<std::string, var> mapParam = convertor.convertParam(xmlParam);
	// call the constructor with the converted arguments
	return self.attr("__init__")(matConnect, mapParam);
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
