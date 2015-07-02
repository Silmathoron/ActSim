#ifndef CONVERT_H
#define CONVERT_H

#include <map>
#include <string>

#include <Python.h>
#include <boost/python.hpp>
#include <boost/variant.hpp>

#include <boost/numeric/ublas/matrix_sparse.hpp>

namespace py = boost::python;

typedef boost::variant<double, std::string, int, bool> var;
typedef std::map<std::string, var>::iterator it_mapParam;



/*
 ***
 * Convertor class
 ***********************/

class Convertor {
	
	public:
		Convertor();
		~Convertor();
		std::map<std::string, var> convertParam(py::object xmlTree);
		int getNumNeurons(py::object csrData);
		std::vector<double> getDataConnectMat(py::object csrData);
		std::vector<size_t> getIndPtrConnectMat(py::object csrData);	
		std::vector<int> getIndicesConnectMat(py::object csrData);
		
	private:
		// python init variables
		py::object m_mainModule;
		py::object m_mainNamespace;
		// base converters
		var castFromString(std::string strType, std::string value);
		bool boolFromString(std::string strValue);
		// complex converters
		py::list vec_to_list(const std::vector<var>& v);
		struct handler : boost::static_visitor<var> {
			var operator()(double d) const;
			var operator()(std::string s) const;
			var operator()(int n) const;
			var operator()(bool b) const;
		};
		// error handling
		std::string parse_python_exception();		
};

//#include "Convertor.tpp" // not useful anymore since I got rid of the template

#endif
