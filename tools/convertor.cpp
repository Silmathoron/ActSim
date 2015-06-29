/*
 ***
 * Py/C++ conversion
 ************************/

#include "convertor.h"

#include <stdexcept>
#include <boost/python/stl_iterator.hpp>


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
    }
    catch(py::error_already_set const &){
        std::string perror_str = parse_python_exception();
        std::cout << "Error in Python initialization: " << perror_str << std::endl;
    }
}

Convertor::~Convertor() {
	try{
        Py_Finalize();
    }
    catch(py::error_already_set const &){
        std::string perror_str = parse_python_exception();
        std::cout << "Error in Py_Finalize: " << perror_str << std::endl;
    }
}


/* *********************** *
 * Basic object conversion *
 * *********************** */

/* variant from string */

var Convertor::castFromString(std::string strType, std::string value) {
	switch(strType)
	{
		case "int":		return var(static_cast<int>(value));
		case "float":	return var(static_cast<float>(value));
		case "string":	return var(value);
		case "bool":	return var(boolFromString(value));
		default:		throw std::invalid_argument(boost::format("Type: " + strType + " is not supported!"));
	}
}

/* string to bool */

bool Convertor::boolFromString(std::string strValue) {
	if (strValue == "true" || strValue == "True") return true;
	else return false;
}


/* ************************ *
 * XML parameter conversion *
 * ************************ */

std::map<std::string, var> convertParam(py::object xmlRoot)
{
	std::map<std::string, var> mapParameters;
	// iterate on all children
	int nSize = py::len(list);
	for (int i=0; i< nSize; ++i) {
		// extract the tag and the name as strings
		py::object child = py::object(xmlRoot[i]);
		std::string tag = py::extract<std::string>(child.tag);
		std::string name = py::extract<std::string>(child.attrib["name"]);
		std::string text = py::extract<std::string>(child.text);
		// get the value
		var value = castFromString(tag, text);
		// assign to the map
		mapParameters[name] = value;
	}
}


/* *********************** *
 * create uBLAS csr matrix *
 * *********************** */

csr Convertor::makeConnectMat(py::object csrData) {
	vector<double> vecData = stdlist_to_vec<double>(csrData[0]);
	vector<int> vecIndPtr = stdlist_to_vec<int>(csrData[1]);
	vector<int> vecIndices = stdlist_to_vec<int>(csrData[2]);
	csr matConnect;
	for (int i=0; i<vecIndices.size(); ++i) {
		for (int j=vecIndPtr[i]; j<vecIndPtr[i+1]; ++j) {
			matConnect(i,vecIndices[j]) = vecData[j];
		}
	}
	return matConnect;
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

/* tovec */

// for a list of extractible boost types
template< typename T >
std::vector<T> Convertor::stdlist_to_vec(const py::object& iterable)
{
	return std::vector<T>(	py::stl_input_iterator<T>(iterable),
							py::stl_input_iterator<T>() );
}

// for a list of py objects (e.g. a list of lists)
std::vector<py::object> pyobjlist_to_vec(py::object& list)
{
	std::vector<T> vec;
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

std::string Convertor::parse_python_exception(){
    PyObject *type_ptr = NULL, *value_ptr = NULL, *traceback_ptr = NULL;
    PyErr_Fetch(&type_ptr, &value_ptr, &traceback_ptr);
    std::string ret("Unfetchable Python error");
    
    if(type_ptr != NULL){
        py::handle<> h_type(type_ptr);
        py::str type_pstr(h_type);
        py::extract<std::string> e_type_pstr(type_pstr);
        if(e_type_pstr.check())
            ret = e_type_pstr();
        else
            ret = "Unknown exception type";
    }
    
    if(traceback_ptr != NULL){
        py::handle<> h_tb(traceback_ptr);
        py::object tb(py::import("traceback"));
        py::object fmt_tb(tb.attr("format_tb"));
        py::object tb_list(fmt_tb(h_tb));
        py::object tb_str(py::str("\n").join(tb_list));
        py::extract<std::string> returned(tb_str);
        if(returned.check())
            ret += ": " + returned();
        else
            ret += std::string(": Unparseable Python traceback");
    }
    return ret;
}
