function SmithAnimator_LLeft(p)
% SMITHANIMATOR_LLEFT  L型(左)匹配电路的 Smith 圆图动态演示
% 拓扑：源(50) -> [串联 L+C2] -> [并联 C1] -> 负载 ZL
% 匹配轨迹顺序(从负载向源)： Load -> 并联 C1 -> 串联(L+C2) -> Source

    %% 1. 初始化窗口与布局
    fig = uifigure('Name', 'Smith圆图匹配过程演示 —— L型(左)', ...
        'Position', [100, 100, 1200, 750], ...
        'Color', 'w', ...
        'CloseRequestFcn', @closeWindow);
    
    g = uigridlayout(fig, [1, 2]);
    g.ColumnWidth = {'2x', '1x'}; 
    
    % 左侧：画图
    pnlPlot = uipanel(g);
    pnlPlot.BorderType = 'none';
    pnlPlot.BackgroundColor = 'w';
    
    % 右侧：控制与文字
    pnlRight = uigridlayout(g, [3, 1]);
    pnlRight.RowHeight = {'1x', '3x', 'fit'};
    pnlRight.Layout.Column = 2;
    
    % 标题与文字
    titleLabel = uilabel(pnlRight);
    titleLabel.FontSize = 24;
    titleLabel.FontWeight = 'bold';
    titleLabel.Text = '解题步骤详解';
    titleLabel.Layout.Row = 1;
    titleLabel.VerticalAlignment = 'bottom';
    
    txtLabel = uilabel(pnlRight);
    txtLabel.VerticalAlignment = 'top';
    txtLabel.WordWrap = 'on';
    txtLabel.FontSize = 16;
    txtLabel.FontName = 'Microsoft YaHei';
    txtLabel.Text = 'L型(左)用于高阻负载匹配。\n请点击下方 [Start] 开始演示...';
    txtLabel.Layout.Row = 2;

    % 控制区
    pnlControls = uipanel(pnlRight);
    pnlControls.Layout.Row = 3;
    pnlControls.BackgroundColor = [0.95 0.95 0.95];
    
    cg = uigridlayout(pnlControls, [2, 3]);
    cg.RowHeight = {'fit', 'fit'};
    cg.Padding = [10 10 10 10];
    
    lblSpeed = uilabel(cg);
    lblSpeed.Text = '演示速度:';
    lblSpeed.Layout.Row = 1; lblSpeed.Layout.Column = [1 3];
    
    sldSpeed = uislider(cg);
    sldSpeed.Layout.Row = 2; sldSpeed.Layout.Column = 1;
    sldSpeed.Limits = [1 100]; sldSpeed.Value = 50;
    
    btnStart = uibutton(cg, 'push', 'Text', 'Start', 'FontWeight', 'bold', ...
        'ButtonPushedFcn', @onStart, 'BackgroundColor', [0.47 0.67 0.19], 'FontColor', 'w');
    btnStart.Layout.Row = 2; btnStart.Layout.Column = 2;

    btnStop = uibutton(cg, 'push', 'Text', 'Stop', 'ButtonPushedFcn', @onStop, ...
        'BackgroundColor', [0.85 0.33 0.1], 'FontColor', 'w', 'Enable', 'off');
    btnStop.Layout.Row = 2; btnStop.Layout.Column = 3;

    btnReset = uibutton(cg, 'push', 'Text', 'Reset', 'ButtonPushedFcn', @onReset);
    btnReset.Layout.Row = 1; btnReset.Layout.Column = 3; 
    
    %% 2. 物理量计算
    w = 2 * pi * p.f;
    Z0 = p.Z0;
    z2g = @(z) (z - Z0) ./ (z + Z0); % 阻抗转反射系数
    
    % --- 关键点计算 ---
    % 1. 起点：负载
    Z_start = p.ZL;
    Y_start = 1 / Z_start;
    
    % 2. 第一段：并联 C1
    % C1 在负载端并联，导纳相加：Y_mid = Y_load + jwC1
    B_C1 = w * p.C1;
    Y_mid = Y_start + 1j * B_C1;
    Z_mid = 1 / Y_mid;
    
    % 3. 第二段：串联 (L + C2)
    % 这是一个串联支路，阻抗相加：Z_end = Z_mid + j(wL - 1/wC2)
    XL = w * p.L;
    XC2 = -1 / (w * p.C2);
    X_series_net = XL + XC2; % 净串联电抗
    
    Z_end = Z_mid + 1j * X_series_net; % 理论上应为 50 + j0
    
    % --- 轨迹点生成 ---
    steps = 100;
    
    % 轨迹 1 (绿色): Load -> 并联 C1
    % 在导纳平面上，电纳 B 从 Imag(Y_start) 增加到 Imag(Y_mid)
    B_vals_1 = linspace(0, B_C1, steps);
    Y_traj1 = Y_start + 1j * B_vals_1;
    Z_traj1 = 1 ./ Y_traj1;
    Traj1_G = z2g(Z_traj1);
    
    % 轨迹 2 (蓝色/品红): C1 -> 串联支路 -> Source
    % 在阻抗平面上，电抗 X 从 Imag(Z_mid) 变化到 0 (匹配点)
    % 变化量就是 X_series_net
    X_vals_2 = linspace(0, X_series_net, steps);
    Z_traj2 = Z_mid + 1j * X_vals_2;
    Traj2_G = z2g(Z_traj2);
    
    % 确定轨迹2的颜色：如果是感性(向上)用品红，容性(向下)用蓝
    if X_series_net >= 0
        colorTraj2 = 'm-'; % Magenta (Inductive)
    else
        colorTraj2 = 'b-'; % Blue (Capacitive)
    end

    %% 3. 绘图初始化
    ax = axes(pnlPlot);
    try
        smithplot(ax, 'GridType', 'ZY', 'Color', [0.8 0.8 0.8]);
    catch
        title(ax, '需安装RF Toolbox');
    end
    hold(ax, 'on');
    title(ax, 'L型(左) 阻抗匹配动态演示');
    
    % 绘图句柄
    hLoad = plot(ax, nan, nan, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % 负载点
    hLine1 = plot(ax, nan, nan, 'g-', 'LineWidth', 2); % 并联轨迹(绿)
    hLine2 = plot(ax, nan, nan, colorTraj2, 'LineWidth', 2); % 串联轨迹
    hEnd = plot(ax, nan, nan, 'kp', 'MarkerSize', 12, 'MarkerFaceColor', 'g'); % 终点
    
    % 状态机
    state.isPlaying = false;
    state.currentPhase = 0; 
    state.idx = 1;
    state.appOpen = true;
    
    %% 4. 动画循环
    while state.appOpen
        if state.isPlaying
            delay = 0.05 - (sldSpeed.Value / 100 * 0.049); 
            pause(delay); 
            updateAnimation();
        else
            pause(0.1);
        end
        drawnow limitrate;
    end
    
    %% 5. 逻辑更新函数
    function updateAnimation()
        switch state.currentPhase
            case 0 % 初始化
                state.currentPhase = 1;
                state.idx = 1;
                
                titleLabel.Text = '步骤 1/3: 标定高阻负载';
                txtLabel.Text = sprintf(['1. 标定负载点。\n' ...
                             'L型(左)要求 R_L > 50Ω。\n\n' ...
                             'Load Z = %.1f %+.1fj Ω'], ...
                             real(p.ZL), imag(p.ZL));
                
            case 1 % 画负载点
                g0 = z2g(Z_start);
                hLoad.XData = real(g0);
                hLoad.YData = imag(g0);
                
                if state.idx > 10 % 停顿
                    state.currentPhase = 2;
                    state.idx = 1;
                    
                    titleLabel.Text = '步骤 2/3: 负载端并联 C1';
                    txtLabel.Text = sprintf(['2. 并联电容 C1 (%.2f pF)。\n\n' ...
                             '原理：沿着等电导圆 (Constant G) 顺时针移动。\n' ...
                             '目的：将等效串联电阻这一实部降低至 50Ω。\n\n' ...
                             '增加电纳 B = +%.4f S'], ...
                             p.C1*1e12, B_C1);
                else
                    state.idx = state.idx + 1;
                end
                
            case 2 % 画并联 C1 轨迹 (绿色)
                if state.idx <= steps
                    hLine1.XData = real(Traj1_G(1:state.idx));
                    hLine1.YData = imag(Traj1_G(1:state.idx));
                    state.idx = state.idx + 1;
                else
                    state.currentPhase = 3;
                    state.idx = 1;
                    
                    % 判断串联支路是感性还是容性
                    if X_series_net >= 0
                        propStr = '感性 (Inductive)';
                    else
                        propStr = '容性 (Capacitive)';
                    end
                    
                    titleLabel.Text = '步骤 3/3: 源端串联 (L+C2)';
                    txtLabel.Text = sprintf(['3. 串联 L 和 C2 组合。\n\n' ...
                             '原理：沿着等电阻圆 (Constant R=1) 移动到圆心。\n' ...
                             'L = %.2f uH, C2 = %.2f pF\n' ...
                             '净电抗 X = %.2f Ω (%s)\n' ...
                             '此时实部已为50Ω，只需抵消虚部。'], ...
                             p.L*1e6, p.C2*1e12, X_series_net, propStr);
                end
                
            case 3 % 画串联轨迹
                if state.idx <= steps
                    hLine2.XData = real(Traj2_G(1:state.idx));
                    hLine2.YData = imag(Traj2_G(1:state.idx));
                    state.idx = state.idx + 1;
                else
                    state.currentPhase = 4;
                    % 画终点
                    hEnd.XData = 0; hEnd.YData = 0;
                    
                    titleLabel.Text = '匹配完成';
                    txtLabel.Text = sprintf('匹配结束！\n最终阻抗 Z = 50 + j0 Ω');
                    
                    state.isPlaying = false;
                    btnStart.Text = 'Finished';
                    btnStart.Enable = 'off';
                    btnStop.Enable = 'off';
                end
        end
    end

    %% 6. 回调函数
    function onStart(~, ~)
        state.isPlaying = true;
        btnStart.Enable = 'off';
        btnStop.Enable = 'on';
        if state.currentPhase == 4, onReset(); state.isPlaying = true; end
    end

    function onStop(~, ~)
        state.isPlaying = false;
        btnStart.Text = 'Continue';
        btnStart.Enable = 'on';
        btnStop.Enable = 'off';
    end

    function onReset(~, ~)
        state.isPlaying = false;
        state.currentPhase = 0;
        state.idx = 1;
        
        hLoad.XData = nan; hLoad.YData = nan;
        hLine1.XData = nan; hLine1.YData = nan;
        hLine2.XData = nan; hLine2.YData = nan;
        hEnd.XData = nan; hEnd.YData = nan;
        
        btnStart.Text = 'Start';
        btnStart.Enable = 'on';
        btnStop.Enable = 'off';
        titleLabel.Text = '解题步骤详解';
        txtLabel.Text = '已重置。请点击 [Start] 开始演示...';
    end

    function closeWindow(~, ~)
        state.appOpen = false;
        delete(fig);
    end
end