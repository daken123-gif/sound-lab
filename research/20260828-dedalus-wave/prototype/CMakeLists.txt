cmake_minimum_required(VERSION 3.16)
project(dedalus_temporal_memory_prototype LANGUAGES CXX)

add_executable(temporal_memory_tests
    TemporalMemoryPrototype.cpp
    TemporalMemoryPrototypeTests.cpp
)

target_compile_features(temporal_memory_tests PRIVATE cxx_std_17)
target_compile_options(temporal_memory_tests PRIVATE
    $<$<CXX_COMPILER_ID:Clang,GNU>:-Wall;-Wextra;-Wpedantic;-Werror>
)

enable_testing()
add_test(NAME temporal_memory_tests COMMAND temporal_memory_tests)
