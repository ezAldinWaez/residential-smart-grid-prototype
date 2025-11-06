# Problem
For n houses sharing the solar plant, we want a way to minimize the waste.

# Parameters
How do we measure that one solution is better or worse? Average Grid Dependency, Wasted Solar Energy.

# Solution 1
Give each house a static and equal virtual battery and distribute the power equally.

# Solution 2
Give each house a dynamic and equal virtual battery in the beginning, and depending on their load over time, reduce or increase the virtual battery.

# Solution 3
Give each house a static and equal virtual battery. It goes like this: it predicts the usage of each house and forecasts the energy to come. When anyone uses more than is allocated, based on the predictions and forecastings, it sees if it can take from some house predicted that it will not need it until the forecasted energy resupplies it and so on. That is, we use other's allocated energy when we can forecast it will be refilled before they need it.

# Solution 4
Give each house initially an equal virtual battery. Based on their prediction until the next solar power refill, it gives away some of its allocation to the pool. When it takes up all its virtual battery, it predicts how much it needs, and it takes it from the pool and re-allocates it to itself. If the pool is empty, and you have allocated less than your fair share (the equal amount). Then you take allocation from someone who exceed it and max out at the equal amount.
