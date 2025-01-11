admin_data = dict(
    email='',
    username='admin',
    password='dailam132@@',
)

post_data = dict(
    id="post",
    title="A plus B",
    description="a + b ok",
    memory_limit=32,
    time_limit=1,
)

generator_source = open("post_generator.cpp").read()
solver_source = open("post_solver.cpp").read()
tests = open("post_tests.txt").read()

post_testdata = dict(
    tests=tests,
    generator=dict(source=generator_source,language="cpp17"),
    solver=dict(source=solver_source,language="cpp17"),
    checker_type="token",
)