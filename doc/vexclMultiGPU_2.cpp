vex::Context ctx( vex::Filter::Any );

std::vector<std::vector<vex::command_queue>> q;
for(size_t d = 0; d < ctx.size(); ++d)
    q.push_back({ctx.queue(d)});


//...

// In a std::thread perhaps:
chunk1(q[d], m * n);
chunk2(q[d], m * n);
// ...
