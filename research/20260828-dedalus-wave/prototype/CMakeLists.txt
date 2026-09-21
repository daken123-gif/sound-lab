cmake_minimum_required(VERSION 3.16)
project(dedalus_temporal_memory_prototype LANGUAGES CXX)

add_executable(temporal_memory_tests
    TemporalMemoryPrototype.cpp
    TemporalMemoryPrototypeTests.cpp
)

add_executable(four_line_fdn_tests
    FourLineFeedbackNetwork.cpp
    FourLineFeedbackNetworkTests.cpp
)

foreach(target temporal_memory_tests four_line_fdn_tests)
    target_compile_features(${target} PRIVATE cxx_std_17)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,GNU>:-Wall;-Wextra;-Wpedantic;-Werror>
    )
endforeach()

enable_testing()
add_test(NAME temporal_memory_tests COMMAND temporal_memory_tests)
add_test(NAME four_line_fdn_tests COMMAND four_line_fdn_tests)
