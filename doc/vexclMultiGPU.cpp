#include <vexcl/vexcl.hpp>

int main() {
    const size_t n = 1024; // Each vector size.
    const size_t m = 4;    // Number of vectors in a chunk.

    vex::Context ctx( vex::Filter::Count(1) );

    // The input vectors...
    vex::vector<double> chunk1(ctx, m * n);
    vex::vector<double> chunk2(ctx, m * n);

    // ... with some data.
    chunk1 = vex::element_index();
    chunk2 = vex::element_index();

    vex::vector<double> gram(ctx, m * m); // The current chunk of Gram matrix to fill.

    /*
     * chunk1 and chunk2 both have dimensions [m][n].
     * We want to take each of chunk2 m rows, subtract those from each of
     * chunk1 rows, and reduce the result along the dimension n.
     *
     * In order to do this, we create two virtual 3D matrices (x and y below,
     * those are just expressions and are never instantiated) sized [m][m][n],
     * where
     *
     *     x[i][j][k] = chunk1[i][k] for each j, and
     *     y[i][j][k] = chunk2[j][k] for each i.
     *
     * Then what we need to compute is
     *
     *     gram[i][j] = sum_k( (x[i][j][k] - y[i][j][k])^2 );
     *
     * Here it goes:
     */
    using vex::extents;

    auto x = vex::reshape(chunk1, extents[m][m][n], extents[0][2]);
    auto y = vex::reshape(chunk2, extents[m][m][n], extents[1][2]);

    // The single OpenCL kernel is generated and launched here:
    gram = vex::reduce<vex::SUM>(
            extents[m][m][n],     // The dimensions of the expression to reduce.
            pow(x - y, 2.0),      // The expression to reduce.
            2                     // The dimension to reduce along.
            );

    // Copy the result to host, spread it across your complete gram matrix.
    // I am lazy though, so let's just dump it to std::cout:
    std::cout << gram << std::endl;
}
