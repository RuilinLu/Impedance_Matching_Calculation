function SmithAnimator_pi1(p)
% SMITHANIMATOR_PI1 [Pi I型电路 - 优化停顿版]
% 对应电路拓扑：负载(ZL) -> [并联 C1] -> [串联 (L+C2)] -> [并联 C3] -> 源(Source)
% 动画顺序：从负载向源端逆向推演

    %% 1. 初始化窗口与布局
    % 使用兼容旧版 MATLAB 的写法
    fig = uifigure('Name', 'Smith圆图演示 —— Pi (I) 型 C-LC-C 电路', ...
        'Position', [100, 100, 1200, 750], ...
        'Color', 'w', ...
        'CloseRequestFcn', @closeWindow);
    
    g = uigridlayout(fig, [1, 2]);
    g.ColumnWidth = {'2x', '1x'}; 
    
    % 左侧：绘图区
    pnlPlot = uipanel(g, 'BorderType', 'none', 'BackgroundColor', 'w');
    
    % 右侧：控制与信息区
    pnlRight = uigridlayout(g, [3, 1]);
    pnlRight.RowHeight = {'1x', '3x', 'fit'};
    pnlRight.Layout.Column = 2;
    
    % 标题 Label
    titleLabel = uilabel(pnlRight, 'FontSize', 22, 'FontWeight', 'bold', ...
        'Text', '匹配步骤详解', 'VerticalAlignment', 'bottom');
    
    % 文本 Label
    txtLabel = uilabel(pnlRight, 'VerticalAlignment', 'top', 'WordWrap', 'on', ...
        'FontSize', 15, 'FontName', 'Microsoft YaHei', ...
        'Text', '初始化...');

    % 控制面板
    pnlControls = uipanel(pnlRight, 'BackgroundColor', [0.95 0.95 0.95]);
    cg = uigridlayout(pnlControls, [2, 3]);
    cg.RowHeight = {'fit', 'fit'};
    cg.Padding = [10 10 10 10];
    
    % 速度控制
    lblSpd = uilabel(cg, 'Text', '演示速度:');
    lblSpd.Layout.Row = 1; lblSpd.Layout.Column = [1 3];
    
    sldSpeed = uislider(cg, 'Limits', [1 100], 'Value', 60);
    sldSpeed.Layout.Row = 2; sldSpeed.Layout.Column = 1;
    
    % 按钮组
    btnStart = uibutton(cg, 'push', 'Text', 'Start', 'FontWeight', 'bold', ...
        'ButtonPushedFcn', @onStart, 'BackgroundColor', [0.47 0.67 0.19], 'FontColor', 'w');
    btnStart.Layout.Row = 2; btnStart.Layout.Column = 2;
        
    btnStop = uibutton(cg, 'push', 'Text', 'Stop', 'ButtonPushedFcn', @onStop, ...
        'BackgroundColor', [0.85 0.33 0.1], 'FontColor', 'w', 'Enable', 'off');
    btnStop.Layout.Row = 2; btnStop.Layout.Column = 3;
    
    btnReset = uibutton(cg, 'push', 'Text', 'Reset', 'ButtonPushedFcn', @onReset);
    btnReset.Layout.Row = 1; btnReset.Layout.Column = 3;
    
    %% 2. 物理量与轨迹计算
    w = 2 * pi * p.f;
    Z0 = p.Z0;
    z2g = @(z) (z - Z0) ./ (z + Z0); % 阻抗 -> 反射系数
    
    % --- 阶段 0: 起点 (负载) ---
    Z_pt0 = p.ZL;
    
    % --- 阶段 1: 并联 C1 (负载端) ---
    Y_pt0 = 1 / Z_pt0;
    Y_pt1 = Y_pt0 + 1j * (w * p.C1);
    Z_pt1 = 1 / Y_pt1; % 转回阻抗
    
    % --- 阶段 2: 串联支路 (L + C2) ---
    X_branch = (w * p.L) - 1/(w * p.C2);
    Z_pt2 = Z_pt1 + 1j * X_branch;
    
    % --- 阶段 3: 并联 C3 (源端) ---
    Y_pt2 = 1 / Z_pt2;
    Y_pt3 = Y_pt2 + 1j * (w * p.C3);
    Z_pt3 = 1 / Y_pt3;
    
    % --- 轨迹数组生成 ---
    steps = 150;
    
    % Traj 1: 并联 C1
    B_C1 = w * p.C1;
    B_vals1 = linspace(0, B_C1, steps);
    Traj1_G = zeros(1, steps);
    for i = 1:steps
        Y_temp = Y_pt0 + 1j * B_vals1(i);
        Traj1_G(i) = z2g(1 / Y_temp);
    end
    
    % Traj 2: 串联 (L+C2)
    X_vals2 = linspace(0, X_branch, steps);
    Traj2_G = z2g(Z_pt1 + 1j * X_vals2);
    
    % Traj 3: 并联 C3
    B_C3 = w * p.C3;
    B_vals3 = linspace(0, B_C3, steps);
    Traj3_G = zeros(1, steps);
    for i = 1:steps
        Y_temp = Y_pt2 + 1j * B_vals3(i);
        Traj3_G(i) = z2g(1 / Y_temp);
    end

    %% 3. 绘图初始化
    ax = axes(pnlPlot);
    try 
        smithplot(ax, 'GridType', 'ZY', 'Color', [0.8 0.8 0.8]); 
    catch
        title(ax, '需安装 RF Toolbox');
    end
    hold(ax, 'on'); 
    title(ax, 'Pi (I) 型混合匹配电路');
    
    % 绘图句柄
    hLoad  = plot(ax, nan, nan, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
    hLine1 = plot(ax, nan, nan, 'b-', 'LineWidth', 2); % 并 C1 (蓝)
    hLine2 = plot(ax, nan, nan, 'g-', 'LineWidth', 2); % 串 L+C2 (绿)
    hLine3 = plot(ax, nan, nan, 'm-', 'LineWidth', 2); % 并 C3 (品红)
    hEnd   = plot(ax, nan, nan, 'kp', 'MarkerSize', 12, 'MarkerFaceColor', 'y');
    
    state.isPlaying = false; 
    state.currentPhase = 0; 
    state.idx = 1; 
    state.appOpen = true;
    
    %% 4. 动画循环
    while state.appOpen
        if state.isPlaying
            delay = 0.04 - (sldSpeed.Value / 100 * 0.038);
            pause(delay); 
            updateAnimation();
        else
            pause(0.1);
        end
        drawnow limitrate;
    end
    
    %% 5. 逻辑更新 (关键修改在这里)
    function updateAnimation()
        switch state.currentPhase
            case 0
                state.currentPhase = 1; 
                % 【关键修改】将初始 idx 设为负数 (例如 -50)。
                % 每次循环 idx 加 1，直到 idx >= 1 才开始画线。
                % 这会产生约 1.5~2 秒的停顿，期间只显示初始文本。
                state.idx = -50; 
                
                titleLabel.Text = '1. 初始负载 & 并联 C1';
                txtLabel.Text = sprintf('起点：负载 ZL = %.1f%+.1fj Ω\n\n准备接入负载端并联电容 C1...', real(Z_pt0), imag(Z_pt0));
                
            case 1 % 画起点 和 C1
                % 无论何时都绘制负载点
                g0 = z2g(Z_pt0);
                hLoad.XData = real(g0); hLoad.YData = imag(g0);
                
                % 【关键修改】如果 idx < 1，说明在停顿期，只更新计数器，不画线，不改文字
                if state.idx < 1
                    state.idx = state.idx + 1;
                    return; % 跳过本帧后续逻辑
                end
                
                % 停顿结束，开始画线
                if state.idx <= steps
                    hLine1.XData = real(Traj1_G(1:state.idx)); 
                    hLine1.YData = imag(Traj1_G(1:state.idx));
                    state.idx = state.idx + 1;
                    
                    % 只有开始动了才改变文字
                    txtLabel.Text = sprintf('正在并联 C1 (%.2f pF)\n沿着等电导圆移动。\n增加电纳 B = +%.4f S', p.C1*1e12, w*p.C1);
                else
                    state.currentPhase = 2; state.idx = 1;
                    titleLabel.Text = '2. 串联 (L+C2) 支路';
                end
                
            case 2 % 画串联 L+C2
                if state.idx <= steps
                    hLine2.XData = real(Traj2_G(1:state.idx)); 
                    hLine2.YData = imag(Traj2_G(1:state.idx));
                    state.idx = state.idx + 1;
                    
                    typeStr = '感性';
                    if X_branch < 0, typeStr = '容性'; end
                    
                    txtLabel.Text = sprintf('串联 (L+C2) 支路\nL=%.1fnH, C2=%.1fpF\n支路净电抗 X=%.1fΩ (%s)\n沿着等电阻圆移动。', ...
                        p.L*1e9, p.C2*1e12, X_branch, typeStr);
                else
                    state.currentPhase = 3; state.idx = 1;
                    titleLabel.Text = '3. 并联 C3 (源端)';
                end
                
            case 3 % 画并联 C3
                if state.idx <= steps
                    hLine3.XData = real(Traj3_G(1:state.idx)); 
                    hLine3.YData = imag(Traj3_G(1:state.idx));
                    state.idx = state.idx + 1;
                    txtLabel.Text = sprintf('正在并联源端电容 C3 (%.2f pF)\n沿着等电导圆移动，\n最终目标是匹配点 (50Ω)。', p.C3*1e12);
                else
                    % 结束
                    gEnd = z2g(Z_pt3);
                    hEnd.XData = real(gEnd); hEnd.YData = imag(gEnd);
                    titleLabel.Text = '匹配完成';
                    txtLabel.Text = sprintf('最终阻抗 Z = %.2f %+.2fj Ω\n驻波比 VSWR = %.2f', ...
                        real(Z_pt3), imag(Z_pt3), (1+abs(gEnd))/(1-abs(gEnd)));
                    state.isPlaying = false;
                    btnStart.Text = 'Finished'; btnStart.Enable = 'off'; btnStop.Enable = 'off';
                end
        end
    end

    %% 6. 回调函数
    function onStart(~,~)
        state.isPlaying = true; btnStart.Enable = 'off'; btnStop.Enable = 'on';
        if state.currentPhase == 3 && state.idx >= steps, onReset(); state.isPlaying = true; end
    end
    function onStop(~,~)
        state.isPlaying = false; btnStart.Text = 'Continue'; btnStart.Enable = 'on'; btnStop.Enable = 'off';
    end
    function onReset(~,~)
        state.isPlaying = false; state.currentPhase = 0; state.idx = 1;
        set([hLoad, hLine1, hLine2, hLine3, hEnd], 'XData', nan, 'YData', nan);
        btnStart.Text = 'Start'; btnStart.Enable = 'on'; btnStop.Enable = 'off';
        titleLabel.Text = '准备开始';
        txtLabel.Text = '点击 Start 开始演示';
    end
    function closeWindow(~,~)
        state.appOpen = false; delete(fig);
    end
end