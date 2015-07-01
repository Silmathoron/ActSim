/*
 * ***
 * Activity simulator for ActSim
 ***********************************/

#include "activitySimulator.hpp"
#include "tools/convertor.hpp"

#include <boost/format.hpp>
#include <math.h>

#include <vexcl/vexcl.hpp>
#include <vexcl/spmat.hpp>


namespace py = boost::python;


/*
 ***
 * Simulator class
 ************************/

/* *********** *
 * Constructor *
 * *********** */

Simulator::Simulator(std::vec<int> vecIndPtr, std::vec<int> vecIndices, std::vec<double> vecData, std::map<std::string, var> mapParam):
	m_vecIndPtr(vecIndPtr), m_vecIndices(vecIndices), m_vecData(vecData), m_mapParam(mapParam)
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
	// initiate openCL
	vex::Context ctx( vex::Filter::Type(CL_DEVICE_TYPE_GPU) && vex::Filter::DoublePrecision );
	if (!ctx) throw std::runtime_error("No devices available.");
	// cpu vectors
	std::vector<double> vecDblEmpty;
	std::vector<double> vecThreshold(m_nNeurons, m_rThreshold);
	std::vector<int> vecZeros(m_nNeurons, 0);
	std::vector<int> vecIntEmpty;
	// initialize on the GPU
	vex::vector<double> d_vecPotential(ctx, vecPotential);
	vex::vector<double> d_vecNoise(ctx, vecPotential);
	vex::vector<double> d_vecThreshold(ctx, vecPotential);
	vex::vector<int> d_vecActive(ctx, vecZeros);
	vex::vector<int> d_vecRefractory(ctx, vecZeros);
	vex::SpMat<double, int> d_matConnect(ctx, m_nNeurons, m_nNeurons, m_vecIndPtr.data(), m_vecIndices.data(), m_vecData.data());
	vex::SpMat<double, int> d_matActionPotentials(ctx, m_nNeurons, m_nNeurons, vecIntEmpty.data(), vecIntEmpty.data(), vecDblEmpty.data());
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
