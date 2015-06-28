/*
 * APy/C++ converter for ActSim, template file
 */

template<class T>
py::list Convertor::vec_to_list(const std::vector<T>& v)
{
	py::object get_iter = py::iterator<std::vector<T> >();
	py::object iter = get_iter(v);
	py::list l(iter);
	return l;
}
