/*
 * ***
 * Activity simulator for ActSim
 ***********************************/

#include "activitySimulator.hpp"

#include <boost/format.hpp>
#include <boost/python/make_constructor.hpp>
#include <boost/python/raw_function.hpp>

#include <math.h>
#include <random>

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


Simulator::Simulator() {
	m_bRunning = false;
}

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
		else if (iter.first == "Leak") m_rLeak = boost::get<double>(iter.second);
		else if (iter.first == "Refrac") m_rRefrac = boost::get<double>(iter.second);
		else if (iter.first == "SimulTime") m_rSimulTime = boost::get<double>(iter.second);
		else if (iter.first == "TimeStep") m_rTimeStep = boost::get<double>(iter.second);
		else if (iter.first == "NoiseStdDev") m_rNoiseStdDev = boost::get<double>(iter.second);
	}
	// compute remaining values
	m_nTotStep = static_cast<int>(floor(m_rSimulTime / m_rTimeStep));
	m_nRefrac = static_cast<int>(floor(m_rRefrac / m_rTimeStep));
	m_rSqrtStep = sqrt(m_rTimeStep);
}


/* ********** *
 * Simulation *
 * ********** */

/* start */

void Simulator::start() {
	if (!m_bRunning) {
		m_bRunning = true;
		std::cout << "Starting run" << std:: endl;
		runSimulation();
	}
}

/* running the simulation */

void Simulator::runSimulation() {
	// initiate openCL
	vex::Context ctx( vex::Filter::Type(CL_DEVICE_TYPE_GPU) && vex::Filter::DoublePrecision );
	if (!ctx) throw std::runtime_error("No devices available.");
	// cpu random number generator
	std::default_random_engine generator;
	std::normal_distribution<double> distribution(0.0,1.0);
	// cpu vectors
	std::vector<double> vecPotential = initPotential();
	std::vector<double> vecRestPotential = initRestPotential();
	std::vector<double> vecThreshold(m_nNeurons, m_rThreshold);
	std::vector<int> vecZeros(m_nNeurons, 0);
	//~ std::vector<double> vecZeros(m_nNeurons, 0.);
	std::cout << "CPU vec initialized" << std::endl;
	// GPU constants
	//~ double rTimeStep = m_rTimeStep;
	VEX_CONSTANT(ts, 0.001);
	VEX_CONSTANT(rts, 0.01);
	VEX_CONSTANT(l, 0.1);
	// random noise generator
	vex::RandomNormal<double> randNorm;
	// GPU vectors
	vex::vector<double> d_vecPotential(ctx, vecPotential);
	vex::vector<double> d_vecRestPotential(ctx, vecRestPotential);
	vex::vector<double> d_vecThreshold(ctx, vecThreshold);
	vex::vector<int> d_vecActive(ctx, vecZeros);
	vex::vector<int> d_vecRefractory(ctx, vecZeros);
	// GPU matrices
	vex::SpMat<double, int, size_t> d_matConnect(ctx.queue(), static_cast<size_t>(m_nNeurons), static_cast<size_t>(m_nNeurons), m_vecIndPtr.data(), m_vecIndices.data(), m_vecData.data());
	vex::SpMat<double, int, size_t> d_matActionPotentials;
	// run
	for (int i = 0; i<m_nTotStep; ++i) {
		std::cout << boost::format("Current step: %1%") % i << std::endl;
		d_vecPotential += ( (d_vecRestPotential - d_vecPotential) * m_rTimeStep + randNorm(vex::element_index(0,m_nNeurons), std::rand()) * m_rSqrtStep ) / m_rLeak;
		
		//~ d_vecPotential += d_vecRestPotential;
		//~ for (int j=0; j<vecPotential.size(); ++j) {
			//~ vecPotential[j] += ( (vecRestPotential[j] - vecPotential[j]) * 0.001 + distribution(generator) *0.01 ) / 0.1;
		//~ }
	}
}

/* action potential gestion */

VEX_FUNCTION(int, apGestion, (vex::SpMat<double, int, size_t>, d_matActionPotentials),
    double sum = 0;
    double myval = val[i];
    for(size_t j = 0; j < n; ++j)
        if (j != i) sum += fabs(val[j] - myval);
    return sum;
    );


/* ************** *
 * Initialization *
 * ************** */

/* Initialize the potentials */

std::vector<double> Simulator::initPotential() {
	std::vector<double> vecPotential(m_nNeurons);
	return vecPotential;
}

std::vector<double> Simulator::initRestPotential() {
	std::vector<double> vecRestPotential(m_nNeurons);
	return vecRestPotential;
}


/* ************* *
 * Communication *
 * ************* */

/* Send the results to DataProcessor */

py::object Simulator::get_results() {
	py::object results;
	return results;
}


/*
 ***
 * Constructor (interface with Python)
 ********************************************/

std::shared_ptr<Simulator> Simulator_py(py::list lstCSR, py::object xmlRoot) {
	// create the convertor and create c++ arguments
	Convertor convertor = Convertor();
	int numNeurons = convertor.getNumNeurons(lstCSR);
	std::vector<double> vecData = convertor.getDataConnectMat(lstCSR);
	std::vector<size_t> vecIndPtr = convertor.getIndPtrConnectMat(lstCSR);
	std::vector<int> vecIndices = convertor.getIndicesConnectMat(lstCSR);
	std::map<std::string, var> mapParam = convertor.convertParam(xmlRoot);
	// call the constructor with the converted arguments
	return std::shared_ptr<Simulator>( 
		new Simulator(numNeurons, vecIndPtr, vecIndices, vecData, mapParam)
	);
}


/*
 ***
 * Python module declaration
 ********************************************/

BOOST_PYTHON_MODULE(libsimulator) {
	// using no_init postpones defining __init__ function
	py::class_<Simulator>("Simulator", py::no_init)
		.def("__init__", py::make_constructor(&Simulator_py))
		.def("setParam", &Simulator::setParam)
		.def("start", &Simulator::start)
	;
}
