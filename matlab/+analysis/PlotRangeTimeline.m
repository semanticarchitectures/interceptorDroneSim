function PlotRangeTimeline(history)
%PLOTRANGETIMELINE Plot target-interceptor range over time.
    tgt = history.TargetPos;
    intc = history.InterceptorPos;
    ranges = hypot(tgt(:, 1) - intc(:, 1), tgt(:, 2) - intc(:, 2));

    figure('Color', 'w');
    plot(history.TimeSeconds, ranges, 'k-', 'LineWidth', 1.8);
    grid on;
    xlabel('Time (s)');
    ylabel('Range (m)');
    title('Target-Interceptor Range vs Time');
end
