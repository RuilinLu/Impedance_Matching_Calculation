classdef Component_Voltage_All < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                matlab.ui.Figure
        GridLayout              matlab.ui.container.GridLayout
        Edit_C3                 matlab.ui.control.NumericEditField
        C3pFLabel               matlab.ui.control.Label
        Edit_VC3                matlab.ui.control.NumericEditField
        C3V_peakLabel           matlab.ui.control.Label
        Edit_Type               matlab.ui.control.EditField
        Label_3                 matlab.ui.control.Label
        Button_Calc             matlab.ui.control.Button
        Edit_I                  matlab.ui.control.NumericEditField
        A_peakEditFieldLabel    matlab.ui.control.Label
        Edit_VL                 matlab.ui.control.NumericEditField
        LV_peakEditFieldLabel   matlab.ui.control.Label
        Edit_VC2                matlab.ui.control.NumericEditField
        C2V_peakEditFieldLabel  matlab.ui.control.Label
        Edit_VC1                matlab.ui.control.NumericEditField
        C1V_peakEditFieldLabel  matlab.ui.control.Label
        Edit_C2                 matlab.ui.control.NumericEditField
        C2pFEditFieldLabel      matlab.ui.control.Label
        Edit_C1                 matlab.ui.control.NumericEditField
        C1pFEditFieldLabel      matlab.ui.control.Label
        Edit_L                  matlab.ui.control.NumericEditField
        LuHEditFieldLabel       matlab.ui.control.Label
        Edit_RL                 matlab.ui.control.NumericEditField
        Label                   matlab.ui.control.Label
        Edit_Freq               matlab.ui.control.NumericEditField
        MHzEditFieldLabel       matlab.ui.control.Label
        Label_Power             matlab.ui.control.Label
        Edit_Power              matlab.ui.control.NumericEditField
        Label_2                 matlab.ui.control.Label
    end

    
    properties (Access = public)
        f_val  % Frequency in MHz
        L_val  % L in uH
        C1_val % C1 in pF
        C2_val % C2 in pF
        C3_val % C3 in pF
        Z_Real_val  % Load Real Part in Ohm
        Z_Im_val    % Load Imaginary Part in Ohm
        Type_val % Circuit Type (1-5)
    end
    
    methods (Access = private)
        
        function calculateVoltage(app)
           % 1. 获取输入功率
            P_watts = app.Edit_Power.Value;
            
            % 2. 参数单位换算
            f = app.f_val * 1e6;  % MHz -> Hz
            w = 2 * pi * f;
            
            L  = app.L_val * 1e-6;   % uH -> H
            C1 = app.C1_val * 1e-12; % pF -> F
            C2 = app.C2_val * 1e-12; % pF -> F
            C3 = app.C3_val * 1e-12; % pF -> F
            
            R_load = app.Z_Real_val; % 负载实部
            X_load = app.Z_Im_val;   % 负载虚部
            
            % 3. 根据电路类型计算
            switch app.Type_val
                
                % =========================================================
                % Type 1: L型 (右) 
                % 结构: 源(50Ω) -> [并联 C1] -> [串联 L + C2 + Z_Load] -> 地
                % =========================================================
                case 1 
                    % A. 计算源端电压 (并联支路电压)
                    % 匹配状态下，源端看进去是 50Ω 纯电阻
                    V_in_rms = sqrt(P_watts * 50);
                    V_in_peak = sqrt(2) * V_in_rms;
                    
                    % B. 计算串联支路的总阻抗 (模值)
                    % 串联支路包括：电感感抗 + 电容容抗 + 负载阻抗(R+jX)
                    % Z_branch = R_load + j(wL - 1/wC2 + X_load)
                    
                    % 计算电容 C2 的容抗 (防止除以0)
                    if C2 > 0
                        Xc2 = -1 / (w * C2);
                    else
                        Xc2 = 0; 
                    end
                    
                    Xl = w * L;
                    
                    % 支路总电抗 X_total
                    X_total_branch = Xl + Xc2 + X_load;
                    
                    % 支路总阻抗模值 |Z| = sqrt(R^2 + X^2)
                    Z_branch_mag = sqrt(R_load^2 + X_total_branch^2);
                    
                    % C. 计算支路电流 (流过 L 和 C2 的真实电流)
                    % I = U / |Z|
                    if Z_branch_mag > 0
                        I_peak = V_in_peak / Z_branch_mag;
                    else
                        I_peak = 0;
                    end
                    
                    % D. 输出结果
                    app.Edit_VC1.Value = V_in_peak;       % C1 直接承受源电压
                    app.Edit_VC2.Value = I_peak * abs(Xc2); % V_c2 = I * Xc2
                    app.Edit_VL.Value  = I_peak * Xl;       % V_L  = I * Xl
                    app.Edit_I.Value   = I_peak;
                    
                    % L型无 C3
                    app.Edit_VC3.Value = 0; 

                % =========================================================
                % Type 2: L型 (左) 
                % 结构: 源(50Ω) -> [串联 L + C2] -> [并联 C1 || Z_Load] -> 地
                % =========================================================
                case 2
                    % A. 计算输入总电流 (即流过 L 和 C2 的串联电流)
                    % 在匹配状态下，整个网络输入阻抗为 50Ω 纯电阻
                    V_in_rms = sqrt(P_watts * 50);
                    V_in_peak = sqrt(2) * V_in_rms;
                    
                    % 串联支路电流直接由源电压驱动
                    I_series_peak = V_in_peak / 50;
                    
                    % B. 计算串联元件电压 (L 和 C2)
                    Xl = w * L;
                    if C2 > 0
                        Xc2 = -1 / (w * C2);
                    else
                        Xc2 = 0;
                    end
                    
                    % V = I * |X|
                    app.Edit_VL.Value  = I_series_peak * Xl;
                    app.Edit_VC2.Value = I_series_peak * abs(Xc2);
                    
                    % C. 计算并联元件电压 (C1)
                    % C1 与负载并联。此处电压即为负载两端电压 V_load
                    % 利用功率守恒计算：功率 P 被输送到负载的电导部分 G_load
                    % P = 0.5 * V_peak^2 * G_load  =>  V_peak = sqrt(2*P / G_load)
                    
                    % 1. 计算负载导纳 Y_L = 1 / (R_L + jX_L)
                    % 注意：如果 R_load 极小，这里电压会很大
                    Z_load_complex = R_load + 1j * X_load;
                    
                    if abs(Z_load_complex) == 0
                        G_load = 0; % 避免除零
                    else
                        Y_load = 1 / Z_load_complex;
                        G_load = real(Y_load); % 取实部电导
                    end
                    
                    % 2. 计算电压
                    if G_load > 0
                        V_load_peak = sqrt(2 * P_watts / G_load);
                    else
                        V_load_peak = 0;
                    end
                    
                    app.Edit_VC1.Value = V_load_peak;
                    
                    % D. 输出电流和 C3
                    app.Edit_I.Value = I_series_peak; % 显示串联支路的主电流
                    app.Edit_VC3.Value = 0; % L型无C3
                % =========================================================
                % Type 3: T型电路
                % 结构: 源(50Ω) -> [串 C3] -> Node -> [串 C1] -> Z_Load
                %                             |
                %                          [并 L + C2] -> 地
                % =========================================================
                case 3
                    % A. 基础源端参数
                    V_in_rms = sqrt(P_watts * 50);
                    V_in_peak = sqrt(2) * V_in_rms;
                    % 匹配时，输入总电流峰值 (流过 C3)
                    I_total_peak = V_in_peak / 50; 
                    
                    % B. 计算各支路阻抗
                    Xc3 = -1 / (w * C3);
                    Xc1 = -1 / (w * C1);
                    Xc2 = -1 / (w * C2);
                    Xl  = w * L;
                    
                    % C. 计算中间节点电压 V_node
                    % V_node = V_in - I_total * Z_C3 (注意是向量减法，取模计算耐压)
                    % 在复数域计算更精确：Z_C3 = -j*Xc3
                    V_node_complex = V_in_peak - (I_total_peak * (1j * Xc3));
                    V_node_peak = abs(V_node_complex);
                    
                    % D. 计算各元件电压
                    % 1. C3 承受电压：输入电压与节点电压之差 (或直接 I * Xc3)
                    app.Edit_VC3.Value = I_total_peak * abs(Xc3);
                    
                    % 2. 并联支路 (L + C2)
                    % 该支路电流 I_shunt = V_node / |jXL + jXC2|
                    Z_shunt_mag = abs(Xl + Xc2);
                    if Z_shunt_mag > 0
                        I_shunt_peak = V_node_peak / Z_shunt_mag;
                    else
                        I_shunt_peak = 0;
                    end
                    app.Edit_VL.Value  = I_shunt_peak * Xl;
                    app.Edit_VC2.Value = I_shunt_peak * abs(Xc2);
                    
                    % 3. 负载支路 (C1 + Z_Load)
                    % 该支路电流 I_load = V_node / |RL + j(XL + XC1)|
                    Z_load_branch_mag = sqrt(R_load^2 + (X_load + Xc1)^2);
                    if Z_load_branch_mag > 0
                        I_load_peak = V_node_peak / Z_load_branch_mag;
                    else
                        I_load_peak = 0;
                    end
                    app.Edit_VC1.Value = I_load_peak * abs(Xc1);
                    
                    % E. 输出参考电流 (取流过 C1 的电流作为输出)
                    app.Edit_I.Value = I_load_peak;
                % =========================================================
                % Type 4: Pi型电路 I (C-LC-C)
                % 结构: 源(50Ω) -> [并 C3] -> [串 L + C2] -> [并 C1] -> Z_Load
                % =========================================================
                case 4
                    % --- A. 计算源端 (C3) 电压 ---
                    % 假设完全匹配，源端看进去是 50Ω。
                    % V_in = sqrt(P * R)
                    V_in_rms = sqrt(P_watts * 50);
                    V_in_peak = sqrt(2) * V_in_rms;
                    
                    % C3 直接并联在输入端，承受输入电压
                    app.Edit_VC3.Value = V_in_peak;

                    % --- B. 计算负载端 (C1) 电压 ---
                    % 利用功率守恒：P = 0.5 * V_out_peak^2 * G_load_node
                    % 负载节点的总导纳 Y_node2 = Y_load + Y_C1
                    % 因为 C1 是纯电抗，所以节点的电导部分 G_node2 等于负载的电导 G_load
                    
                    Z_load_complex = R_load + 1j * X_load;
                    
                    if abs(Z_load_complex) == 0
                        G_load = 0; % 防止短路除以零
                    else
                        Y_load = 1 / Z_load_complex;
                        G_load = real(Y_load); % 取实部
                    end
                    
                    % 计算输出节点峰值电压
                    if G_load > 1e-9 % 设置一个极小阈值防止除以0
                        V_out_peak = sqrt(2 * P_watts / G_load);
                    else
                        V_out_peak = 0; % 纯电抗负载不消耗有功，理论电压无穷大，此处置0或需保护
                    end
                    
                    % C1 并联在负载端，承受输出电压
                    app.Edit_VC1.Value = V_out_peak;

                    % --- C. 计算中间串联支路 (L + C2) 的电流 ---
                    % 流入负载节点的电流 I_series 提供了负载电流和 C1 的电流
                    % I_series = V_out_node * |Y_node2_total|
                    % Y_node2_total = (1/Z_load) + j(wC1)
                    
                    Y_C1 = 1j * w * C1;
                    Y_node2_total = (1 / Z_load_complex) + Y_C1;
                    
                    I_series_peak = V_out_peak * abs(Y_node2_total);
                    
                    % 此电流即为流过 L 和 C2 的电流
                    app.Edit_I.Value = I_series_peak;

                    % --- D. 计算 L 和 C2 的电压 ---
                    Xl = w * L;
                    if C2 > 0
                        Xc2 = -1 / (w * C2);
                    else
                        Xc2 = 0;
                    end
                    
                    app.Edit_VL.Value  = I_series_peak * Xl;       % V = I * XL
                    app.Edit_VC2.Value = I_series_peak * abs(Xc2); % V = I * XC
                % =========================================================
                % Type 5: Pi型电路 II (源端调节型)
                % 结构: 源(50Ω) -> [并 C1] -> [串 L + C2] -> [并 C3] -> Z_Load
                % =========================================================
                case 5
                    % --- A. 计算源端 (C1) 电压 ---
                    % C1 位于源端。匹配状态下，输入阻抗为 50Ω。
                    % V_in_peak = sqrt(2 * P * 50)
                    V_in_rms = sqrt(P_watts * 50);
                    V_in_peak = sqrt(2) * V_in_rms;
                    
                    % C1 承受源端电压
                    app.Edit_VC1.Value = V_in_peak;
                    
                    % --- B. 计算负载端 (C3) 电压 ---
                    % C3 位于负载端，与 Z_Load 并联。
                    % 功率 P 仅由负载实部消耗。
                    % P = 0.5 * V_out_peak^2 * G_load
                    
                    Z_load_complex = R_load + 1j * X_load;
                    
                    if abs(Z_load_complex) == 0
                        G_load = 0;
                    else
                        Y_load = 1 / Z_load_complex;
                        G_load = real(Y_load); % 负载电导
                    end
                    
                    % 计算负载节点电压 (即 C3 两端电压)
                    if G_load > 1e-9
                        V_out_peak = sqrt(2 * P_watts / G_load);
                    else
                        V_out_peak = 0; % 纯电抗负载需特殊处理
                    end
                    
                    app.Edit_VC3.Value = V_out_peak;
                    
                    % --- C. 计算中间串联支路 (L + C2) 电流 ---
                    % 串联支路电流 I 流入负载端节点，分为流向 C3 的电流和流向 Load 的电流
                    % I_series = V_out_node * |Y_node_total|
                    % Y_node_total = Y_load + Y_C3
                    
                    Y_C3 = 1j * w * C3;
                    Y_load_node_total = (1 / Z_load_complex) + Y_C3;
                    
                    I_series_peak = V_out_peak * abs(Y_load_node_total);
                    
                    app.Edit_I.Value = I_series_peak;
                    
                    % --- D. 计算 L 和 C2 电压 ---
                    % V = I_series * |X|
                    Xl = w * L;
                    if C2 > 0
                        Xc2 = -1 / (w * C2);
                    else
                        Xc2 = 0;
                    end
                    
                    app.Edit_VL.Value  = I_series_peak * Xl;
                    app.Edit_VC2.Value = I_series_peak * abs(Xc2);
                otherwise
                    uialert(app.UIFigure, '未知的电路类型', '错误');
            end
        end
        
        function updateUIForType(app)
            % 根据 Type_val 更新标题和显示内容
            switch app.Type_val
                case 1
                    app.Edit_Type.Value = 'L型电路 (右)';
                    % 隐藏 C3 相关控件
                    app.Label_C3.Visible = 'off';
                    app.Edit_C3.Visible = 'off';
                    app.Label_VC3.Visible = 'off';
                    app.Edit_VC3.Visible = 'off';
                    
                case 2
                    app.Edit_Type.Value = 'L型电路 (左)';
                    % 隐藏 C3
                    app.Label_C3.Visible = 'off';
                    app.Edit_C3.Visible = 'off';
                    app.Label_VC3.Visible = 'off';
                    app.Edit_VC3.Visible = 'off';
                    
                case 3
                    app.Edit_Type.Value = 'T型电路';
                    % 显示 C3
                    app.Label_C3.Visible = 'on';
                    app.Edit_C3.Visible = 'on';
                    app.Label_VC3.Visible = 'on';
                    app.Edit_VC3.Visible = 'on';
                    
                case 4
                    app.Edit_Type.Value = 'Pi型电路 I';
                    % 显示 C3
                    app.Label_C3.Visible = 'on';
                    app.Edit_C3.Visible = 'on';
                    app.Label_VC3.Visible = 'on';
                    app.Edit_VC3.Visible = 'on';
                    
                case 5
                    app.Edit_Type.Value = 'Pi型电路 II';
                    % 显示 C3
                    app.Label_C3.Visible = 'on';
                    app.Edit_C3.Visible = 'on';
                    app.Label_VC3.Visible = 'on';
                    app.Edit_VC3.Visible = 'on';
            end
        end
    end
    

    % Callbacks that handle component events
    methods (Access = private)

        % Code that executes after component creation
        function startupFcn(app, f, L, C1, C2, C3, Z_Real, Z_Im, Type)
           % 1. 存储参数
            app.f_val = f;
            app.L_val = L;
            app.C1_val = C1;
            app.C2_val = C2;
            app.C3_val = C3;
            app.Z_Real_val = Z_Real; % 存储实部
            app.Z_Im_val = Z_Im;     % 存储虚部
            app.Type_val = Type;
            
            % 2. 更新界面只读参数
            app.Edit_Freq.Value = f;
            app.Edit_L.Value = L;
            app.Edit_C1.Value = C1;
            app.Edit_C2.Value = C2;
            app.Edit_C3.Value = C3;
            
            % 界面上只显示实部作为参考，或者您可以修改界面显示复数
            app.Edit_RL.Value = Z_Real; 
            
            % 3. 调整界面布局
            updateUIForType(app);
            
            % 4. 初始计算
            calculateVoltage(app);
        end

        % Button pushed function: Button_Calc
        function Button_CalcPushed(app, event)
            calculateVoltage(app);% 只有按下此按钮时，才会触发 calculateVoltage
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Position = [100 100 792 789];
            app.UIFigure.Name = 'MATLAB App';

            % Create GridLayout
            app.GridLayout = uigridlayout(app.UIFigure);
            app.GridLayout.ColumnWidth = {'1x', '1x', '1x'};
            app.GridLayout.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};

            % Create Label_2
            app.Label_2 = uilabel(app.GridLayout);
            app.Label_2.HorizontalAlignment = 'center';
            app.Label_2.FontSize = 18;
            app.Label_2.FontWeight = 'bold';
            app.Label_2.Layout.Row = 1;
            app.Label_2.Layout.Column = [1 3];
            app.Label_2.Text = '元件耐压计算';

            % Create Edit_Power
            app.Edit_Power = uieditfield(app.GridLayout, 'numeric');
            app.Edit_Power.Limits = [0 Inf];
            app.Edit_Power.FontSize = 18;
            app.Edit_Power.Layout.Row = 2;
            app.Edit_Power.Layout.Column = 2;
            app.Edit_Power.Value = 500;

            % Create Label_Power
            app.Label_Power = uilabel(app.GridLayout);
            app.Label_Power.HorizontalAlignment = 'center';
            app.Label_Power.FontSize = 18;
            app.Label_Power.Layout.Row = 2;
            app.Label_Power.Layout.Column = 1;
            app.Label_Power.Text = '输入功率 (W):';

            % Create MHzEditFieldLabel
            app.MHzEditFieldLabel = uilabel(app.GridLayout);
            app.MHzEditFieldLabel.HorizontalAlignment = 'center';
            app.MHzEditFieldLabel.FontSize = 18;
            app.MHzEditFieldLabel.Layout.Row = 3;
            app.MHzEditFieldLabel.Layout.Column = 1;
            app.MHzEditFieldLabel.Text = '频率 (MHz)';

            % Create Edit_Freq
            app.Edit_Freq = uieditfield(app.GridLayout, 'numeric');
            app.Edit_Freq.Limits = [0 133];
            app.Edit_Freq.Editable = 'off';
            app.Edit_Freq.FontSize = 18;
            app.Edit_Freq.Layout.Row = 3;
            app.Edit_Freq.Layout.Column = 2;
            app.Edit_Freq.Value = 1;

            % Create Label
            app.Label = uilabel(app.GridLayout);
            app.Label.HorizontalAlignment = 'center';
            app.Label.FontSize = 18;
            app.Label.Layout.Row = 4;
            app.Label.Layout.Column = 1;
            app.Label.Text = '负载实部 (Ω)';

            % Create Edit_RL
            app.Edit_RL = uieditfield(app.GridLayout, 'numeric');
            app.Edit_RL.Limits = [0 Inf];
            app.Edit_RL.Editable = 'off';
            app.Edit_RL.FontSize = 18;
            app.Edit_RL.Layout.Row = 4;
            app.Edit_RL.Layout.Column = 2;

            % Create LuHEditFieldLabel
            app.LuHEditFieldLabel = uilabel(app.GridLayout);
            app.LuHEditFieldLabel.HorizontalAlignment = 'center';
            app.LuHEditFieldLabel.FontSize = 18;
            app.LuHEditFieldLabel.Layout.Row = 5;
            app.LuHEditFieldLabel.Layout.Column = 1;
            app.LuHEditFieldLabel.Text = '电感 L (uH)';

            % Create Edit_L
            app.Edit_L = uieditfield(app.GridLayout, 'numeric');
            app.Edit_L.Limits = [0 Inf];
            app.Edit_L.Editable = 'off';
            app.Edit_L.FontSize = 18;
            app.Edit_L.Layout.Row = 5;
            app.Edit_L.Layout.Column = 2;

            % Create C1pFEditFieldLabel
            app.C1pFEditFieldLabel = uilabel(app.GridLayout);
            app.C1pFEditFieldLabel.HorizontalAlignment = 'center';
            app.C1pFEditFieldLabel.FontSize = 18;
            app.C1pFEditFieldLabel.Layout.Row = 6;
            app.C1pFEditFieldLabel.Layout.Column = 1;
            app.C1pFEditFieldLabel.Text = '电容 C1 (pF)';

            % Create Edit_C1
            app.Edit_C1 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_C1.Editable = 'off';
            app.Edit_C1.FontSize = 18;
            app.Edit_C1.Layout.Row = 6;
            app.Edit_C1.Layout.Column = 2;

            % Create C2pFEditFieldLabel
            app.C2pFEditFieldLabel = uilabel(app.GridLayout);
            app.C2pFEditFieldLabel.HorizontalAlignment = 'center';
            app.C2pFEditFieldLabel.FontSize = 18;
            app.C2pFEditFieldLabel.Layout.Row = 7;
            app.C2pFEditFieldLabel.Layout.Column = 1;
            app.C2pFEditFieldLabel.Text = '电容 C2 (pF)';

            % Create Edit_C2
            app.Edit_C2 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_C2.Editable = 'off';
            app.Edit_C2.FontSize = 18;
            app.Edit_C2.Layout.Row = 7;
            app.Edit_C2.Layout.Column = 2;

            % Create C1V_peakEditFieldLabel
            app.C1V_peakEditFieldLabel = uilabel(app.GridLayout);
            app.C1V_peakEditFieldLabel.HorizontalAlignment = 'center';
            app.C1V_peakEditFieldLabel.FontSize = 18;
            app.C1V_peakEditFieldLabel.Layout.Row = 11;
            app.C1V_peakEditFieldLabel.Layout.Column = 1;
            app.C1V_peakEditFieldLabel.Text = 'C1 耐压 (V_peak)';

            % Create Edit_VC1
            app.Edit_VC1 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_VC1.Editable = 'off';
            app.Edit_VC1.FontSize = 18;
            app.Edit_VC1.Layout.Row = 11;
            app.Edit_VC1.Layout.Column = 2;

            % Create C2V_peakEditFieldLabel
            app.C2V_peakEditFieldLabel = uilabel(app.GridLayout);
            app.C2V_peakEditFieldLabel.HorizontalAlignment = 'center';
            app.C2V_peakEditFieldLabel.FontSize = 18;
            app.C2V_peakEditFieldLabel.Layout.Row = 12;
            app.C2V_peakEditFieldLabel.Layout.Column = 1;
            app.C2V_peakEditFieldLabel.Text = 'C2 耐压 (V_peak)';

            % Create Edit_VC2
            app.Edit_VC2 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_VC2.Editable = 'off';
            app.Edit_VC2.FontSize = 18;
            app.Edit_VC2.Layout.Row = 12;
            app.Edit_VC2.Layout.Column = 2;

            % Create LV_peakEditFieldLabel
            app.LV_peakEditFieldLabel = uilabel(app.GridLayout);
            app.LV_peakEditFieldLabel.HorizontalAlignment = 'center';
            app.LV_peakEditFieldLabel.FontSize = 18;
            app.LV_peakEditFieldLabel.Layout.Row = 10;
            app.LV_peakEditFieldLabel.Layout.Column = 1;
            app.LV_peakEditFieldLabel.Text = 'L 耐压 (V_peak)';

            % Create Edit_VL
            app.Edit_VL = uieditfield(app.GridLayout, 'numeric');
            app.Edit_VL.Editable = 'off';
            app.Edit_VL.FontSize = 18;
            app.Edit_VL.Layout.Row = 10;
            app.Edit_VL.Layout.Column = 2;

            % Create A_peakEditFieldLabel
            app.A_peakEditFieldLabel = uilabel(app.GridLayout);
            app.A_peakEditFieldLabel.HorizontalAlignment = 'center';
            app.A_peakEditFieldLabel.FontSize = 18;
            app.A_peakEditFieldLabel.Layout.Row = 14;
            app.A_peakEditFieldLabel.Layout.Column = 1;
            app.A_peakEditFieldLabel.Text = '支路电流 (A_peak)';

            % Create Edit_I
            app.Edit_I = uieditfield(app.GridLayout, 'numeric');
            app.Edit_I.Editable = 'off';
            app.Edit_I.FontSize = 18;
            app.Edit_I.Layout.Row = 14;
            app.Edit_I.Layout.Column = 2;

            % Create Button_Calc
            app.Button_Calc = uibutton(app.GridLayout, 'push');
            app.Button_Calc.ButtonPushedFcn = createCallbackFcn(app, @Button_CalcPushed, true);
            app.Button_Calc.FontSize = 18;
            app.Button_Calc.Layout.Row = 9;
            app.Button_Calc.Layout.Column = 1;
            app.Button_Calc.Text = '计算';

            % Create Label_3
            app.Label_3 = uilabel(app.GridLayout);
            app.Label_3.HorizontalAlignment = 'center';
            app.Label_3.FontSize = 24;
            app.Label_3.Layout.Row = 9;
            app.Label_3.Layout.Column = 2;
            app.Label_3.Text = '此次运行的类型：';

            % Create Edit_Type
            app.Edit_Type = uieditfield(app.GridLayout, 'text');
            app.Edit_Type.HorizontalAlignment = 'center';
            app.Edit_Type.FontSize = 20;
            app.Edit_Type.Layout.Row = 9;
            app.Edit_Type.Layout.Column = 3;

            % Create C3V_peakLabel
            app.C3V_peakLabel = uilabel(app.GridLayout);
            app.C3V_peakLabel.HorizontalAlignment = 'center';
            app.C3V_peakLabel.FontSize = 18;
            app.C3V_peakLabel.Layout.Row = 13;
            app.C3V_peakLabel.Layout.Column = 1;
            app.C3V_peakLabel.Text = 'C3 耐压 (V_peak)';

            % Create Edit_VC3
            app.Edit_VC3 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_VC3.Editable = 'off';
            app.Edit_VC3.FontSize = 18;
            app.Edit_VC3.Layout.Row = 13;
            app.Edit_VC3.Layout.Column = 2;

            % Create C3pFLabel
            app.C3pFLabel = uilabel(app.GridLayout);
            app.C3pFLabel.HorizontalAlignment = 'center';
            app.C3pFLabel.FontSize = 18;
            app.C3pFLabel.Layout.Row = 8;
            app.C3pFLabel.Layout.Column = 1;
            app.C3pFLabel.Text = '电容 C3 (pF)';

            % Create Edit_C3
            app.Edit_C3 = uieditfield(app.GridLayout, 'numeric');
            app.Edit_C3.Editable = 'off';
            app.Edit_C3.FontSize = 18;
            app.Edit_C3.Layout.Row = 8;
            app.Edit_C3.Layout.Column = 2;

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = Component_Voltage_All(varargin)

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            % Execute the startup function
            runStartupFcn(app, @(app)startupFcn(app, varargin{:}))

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end