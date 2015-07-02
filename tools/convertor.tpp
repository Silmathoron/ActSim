/*
 * A Py/C++ converter for ActSim, template file
 */
 
//# include "convertor.hpp"

// for a list of extractible boost types
template< typename T >
std::vector<T> Convertor::stdlist_to_vec(const py::object& iterable)
{
	return std::vector<T>(	py::stl_input_iterator<T>(iterable),
							py::stl_input_iterator<T>() );
}
