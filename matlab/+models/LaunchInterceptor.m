function interceptor = LaunchInterceptor(interceptor, heading)
%LAUNCHINTERCEPTOR Launch interceptor toward an initial heading.
    interceptor.state = "LAUNCHED";
    interceptor.heading = heading;
    interceptor.speed = interceptor.maxSpeed;
    interceptor.flightTime = 0.0;
end
