﻿/*
 * ***
 * Activity simulator for ActSim
 ***********************************/

#include "activitySimulator.hpp"

#include <boost/format.hpp>
#include <boost/python/make_constructor.hpp>
#include <boost/python/raw_function.hpp>

#include <math.h>

#include <vexcl/vexcl.hpp>
#include <vexcl/spmat.hpp>


namespace py = boost::python;
namespace ublas = boost::numeric::ublas


/*
 ***
 * Simulator class
 ************************/

/* *********** *
 * Constructor *
 * *********** */


Simulator::Simulator(int numNeurons, std::vector<size_t> vecIndPtr, std::vector<int> vecIndices, std::vector<double> vecData, std::map<std::string, var> mapParam):
	m_nNeurons(numNeurons), m_vecIndPtr(vecIndPtr), m_vecIndices(vecIndices), m_vecData(vecData), m_mapParam(mapParam) {
	m_bRunning = false;
}

Simulator::~Simulator() {}

/* ************** *
 * Set parameters *
 * ************** */

void Simulator::setParam() {
	// load parameters
	for(const auto& iter : m_mapParam) {
		if (iter.first == "Threshold") m_rThreshold = boost::get<double>(iter.second);
		else if (iter.first == "IntCst") m_rIntCst = boost::get<double>(iter.second);
		else if (iter.first == "Leak") m_rLeak = boost::get<double>(iter.second);
		else if (iter.first == "Refrac") m_rRefrac = boost::get<double>(iter.second);
		else if (iter.first == "SimulTime") m_rSimulTime = boost::get<double>(iter.second);
		else if (iter.first == "TimeStep") m_rTimeStep = boost::get<double>(iter.second);
	}
	// compute remaining values
	m_nTotStep = static_cast<int>(floor(m_rSimulTime / m_rTimeStep));
	m_nRefrac = static_cast<int>(floor(m_rRefrac / m_rTimeStep));
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
	std::vector<double> vecPotential = initPotential();
	std::vector<double> vecThreshold(m_nNeurons, m_rThreshold);
	std::vector<int> vecZeros(m_nNeurons, 0);
	// initialize on the GPU
	vex::vector<double> d_vecPotential(ctx, vecPotential);
	vex::vector<double> d_vecNoise(ctx, vecPotential);
	vex::vector<double> d_vecThreshold(ctx, vecPotential);
	vex::vector<int> d_vecActive(ctx, vecZeros);
	vex::vector<int> d_vecRefractory(ctx, vecZeros);
	vex::SpMat<double, int, size_t> d_matConnect(ctx.queue(), static_cast<size_t>(m_nNeurons), static_cast<size_t>(m_nNeurons), m_vecIndPtr.data(), m_vecIndices.data(), m_vecData.data());
	vex::SpMat<double, int, size_t> d_matActionPotentials;
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

/* Initialize the potentials */

std::vector<double> Simulator::initPotential() {
	std::vector<double> vecPotential(m_nNeurons);
	return vecPotential;
}


/*
 ***
 * Raw constructor (interface with Python)
 ********************************************/

py::object Simulator_init(py::tuple args, py::dict kwargs) {
	// create the convertor and create c++ arguments
	py::object self = args[0];
	py::object csrData = args[1];
	py::object xmlParam = args[2];
	Convertor convertor = Convertor();
	int numNeurons = convertor.getNumNeurons(csrData);
	std::vector<double> vecData = convertor.getDataConnectMat(csrData);
	std::vector<size_t> vecIndPtr = convertor.getIndPtrConnectMat(csrData);
	std::vector<int> vecIndices = convertor.getIndicesConnectMat(csrData);
	std::map<std::string, var> mapParam = convertor.convertParam(xmlParam);
	// call the constructor with the converted arguments
	return self.attr("__init__")(vecData, vecIndPtr, vecIndices, mapParam);
}


/*
 ***
 * Python module declaration
 ********************************************/

BOOST_PYTHON_MODULE(simulator) {
	// using no_init postpones defining __init__ function until after
	// raw_function for proper overload resolution order, since later
	// defs get higher priority.
	py::class_<Simulator>("Simulator", py::no_init)
		.def("__init__", py::raw_function(Simulator_init), "simulator")
		.def(py::init<int, std::vector<size_t>, std::vector<int>, std::vector<double>, std::map<std::string, var>>()); // C++ constructor, shadowed by raw ctor
		//.def_readwrite("number", &A::number_)
}
