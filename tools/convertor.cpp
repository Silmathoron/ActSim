/*
 ***
 * Py/C++ conversion
 ************************/

#include "convertor.hpp"

#include <iostream>
#include <stdexcept>


/* ************************ *
 * Generator and destructor *
 * ************************ */

Convertor::Convertor() {
	// init python
	try{
        Py_Initialize();
		m_mainModule = py::import("__main__");
		m_mainNamespace = m_mainModule.attr("__dict__");
		m_mainNamespace["sys"] = py::import("sys");
		// import xml.etree.ElementTree
		//~ m_mainNamespace["xmlet"] = py::import("import xml.etree.ElementTree");
		//~ py::exec("class xmlet.Element(): pass\n",m_mainNamespace);
    }
    catch(py::error_already_set const &){
        std::string perror_str = parse_python_exception();
        std::cout << "Error in Python initialization: " << perror_str << std::endl;
    }
}

Convertor::~Convertor() {
	//~ try{
        //~ Py_Finalize();
    //~ }
    //~ catch(py::error_already_set const &){
        //~ std::string perror_str = parse_python_exception();
        //~ std::cout << "Error in Py_Finalize: " << perror_str << std::endl;
    //~ }
}


/* *********************** *
 * Basic object conversion *
 * *********************** */

/* variant from string */

var Convertor::castFromString(std::string strType, std::string value) {
	if (strType == "int") return var(std::stoi(value));
	else if (strType == "float") return var(std::stod(value));
	else if (strType == "string") return var(value);
	else if (strType == "bool") return var(boolFromString(value));
	else throw std::invalid_argument("Type is not supported!");
}

/* string to bool */

bool Convertor::boolFromString(std::string strValue) {
	if (strValue == "true" || strValue == "True") return true;
	else return false;
}


/* ************************ *
 * XML parameter conversion *
 * ************************ */

std::map<std::string, var> Convertor::convertParam(py::object xmlRoot)
{
	std::map<std::string, var> mapParameters;
	// iterate on all children
	int nSize = py::len(xmlRoot);
	for (int i=0; i< nSize; ++i) {
		// extract the tag and the name as strings
		py::object child = py::object(xmlRoot[i]);
		int nSubSize = py::len(child);
		for (int j=0; j<nSubSize; ++j) {
			py::object subChild = py::object(child[j]);
			std::string tag = py::extract<std::string>(subChild.attr("tag"));
			std::string name = py::extract<std::string>(subChild.attr("attrib")["name"]);
			std::string text = py::extract<std::string>(subChild.attr("text"));
			// get the value
			var value = castFromString(tag, text);
			// assign to the map
			mapParameters[name] = value;
		}
	}
	return mapParameters;
}


/* ******************************* *
 * return array to make csr matrix *
 * ******************************* */

int Convertor::getNumNeurons(py::object csrData) {
	return py::extract<int>(csrData[0]);
}

std::vector<double> Convertor::getDataConnectMat(py::object csrData) {
	return stdlist_to_vec<double>(csrData[3]);
}

std::vector<size_t> Convertor::getIndPtrConnectMat(py::object csrData) {
	return stdlist_to_vec<size_t>(csrData[1]);
}

std::vector<int> Convertor::getIndicesConnectMat(py::object csrData) {
	return stdlist_to_vec<int>(csrData[2]);
}


/* *********************** *
 * List/vector conversions *
 * *********************** */

/* tolist */

py::list Convertor::vec_to_list(const std::vector<var>& v)
{
    py::object get_iter = py::iterator< std::vector<var> >();
    py::object iter = get_iter(v);
    py::list l(iter);
    return l;
}

/* tovec */ //see also convertor.tpp

// for a list of py objects (e.g. a list of lists)
std::vector<py::object> pyobjlist_to_vec(py::object& list)
{
	std::vector<py::object> vec;
	int nSize = py::len(list);
	for (int i=0; i< nSize; ++i) {
		py::object newobj = py::object(list[i]);
		vec.push_back(newobj);
	}
	return vec;
}



/* ************** *
 * Error handling *
 * **************** */

std::string Convertor::parse_python_exception() {
    PyObject *type_ptr = NULL, *value_ptr = NULL, *traceback_ptr = NULL;
    PyErr_Fetch(&type_ptr, &value_ptr, &traceback_ptr);
    std::string ret("Unfetchable Python error");
    
    if(type_ptr != NULL) {
        py::handle<> h_type(type_ptr);
        py::str type_pstr(h_type);
        py::extract<std::string> e_type_pstr(type_pstr);
        if(e_type_pstr.check()) ret = e_type_pstr();
        else ret = "Unknown exception type";
    }
    
    if(traceback_ptr != NULL) {
        py::handle<> h_tb(traceback_ptr);
        py::object tb(py::import("traceback"));
        py::object fmt_tb(tb.attr("format_tb"));
        py::object tb_list(fmt_tb(h_tb));
        py::object tb_str(py::str("\n").join(tb_list));
        py::extract<std::string> returned(tb_str);
        if(returned.check()) ret += ": " + returned();
        else ret += std::string(": Unparseable Python traceback");
    }
    return ret;
}
