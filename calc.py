#/usr/bin/env python
# vim:set ts=4 sw=4 et smartindent fileencoding=utf-8:
'''
wx Calc
'''
import wx
import wx.lib.buttons as Button
from sympy import S
from sympy.core.sympify import SympifyError

class main_frame(wx.Frame):
    '''メイン画面作成'''
    calculation = [] # 計算式格納用
    input_num = [] # 数字格納用
    effective_digit = 0 # 有効桁数
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.make_button()
        self.make_text_panel()

        panel = self.make_panel()
        self.SetSizerAndFit(panel)
        # イベントを設定
        self.Bind(wx.EVT_CHAR, self.on_char)
        # フォーカスは出力に持ってきておく
        self.result_panel.SetFocus()
        # 初期化
        self.clear_calc()

    BUTTON_LABELS = 'Ｃ＋－×÷１２３４５６７８９０＝．'
    def make_button(self):
        '''ボタンを作成する'''
        parent = self
        btn = []
        for v in self.BUTTON_LABELS:
            btn.append(Button.GenButton(parent, label=v))
        # font変更
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=u'メイリオ')
        for v in btn:
            v.SetFont(font)
            v.SetBezelWidth(5)
            v.SetMinSize(wx.DefaultSize)
            # 親にイベントを渡す
            v.Bind(wx.EVT_CHAR, lambda x: wx.PostEvent(parent, x))
            v.Bind(wx.EVT_LEFT_UP, self.btn_press)
        
        self.btn = btn

    def make_text_panel(self):
        '''結果出力用パネルを作る'''
        parent = self
        rslt = wx.TextCtrl(self, wx.ID_ANY, u'0',
            wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.TE_RIGHT)
        rslt.SetInsertionPointEnd()

        font = wx.Font(24, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=u'メイリオ')
        rslt.SetFont(font)
        rslt.SetBackgroundColour(wx.BLACK)
        rslt.SetForegroundColour(wx.WHITE)
        rslt.Bind(wx.EVT_CHAR, lambda x: wx.PostEvent(parent, x))
        self.result_panel = rslt

    def make_panel(self):
        '''メインパネルの作成'''
        layout = wx.GridBagSizer(5, 5)
        layout_flag = wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE
        btn = self.btn
        layout.Add(self.result_panel, (0, 0), (1, 4), flag=layout_flag)
        layout.Add(btn[0], (1, 0), (1, 1), flag=layout_flag)
        layout.Add(btn[3], (1, 2), (1, 1), flag=layout_flag)
        layout.Add(btn[4], (1, 1), (1, 1), flag=layout_flag)
        layout.Add(btn[2], (1, 3), (1, 1), flag=layout_flag)
        layout.Add(btn[11], (2, 0), (1, 1), flag=layout_flag)
        layout.Add(btn[12], (2, 1), (1, 1), flag=layout_flag)
        layout.Add(btn[13], (2, 2), (1, 1), flag=layout_flag)
        layout.Add(btn[1], (2, 3), (2, 1), flag=layout_flag)
        layout.Add(btn[8], (3, 0), (1, 1), flag=layout_flag)
        layout.Add(btn[9], (3, 1), (1, 1), flag=layout_flag)
        layout.Add(btn[10], (3, 2), (1, 1), flag=layout_flag)
        layout.Add(btn[5], (4, 0), (1, 1), flag=layout_flag)
        layout.Add(btn[6], (4, 1), (1, 1), flag=layout_flag)
        layout.Add(btn[7], (4, 2), (1, 1), flag=layout_flag)
        layout.Add(btn[15], (4, 3), (2, 1), flag=layout_flag)
        layout.Add(btn[14], (5, 0), (1, 2), flag=layout_flag)
        layout.Add(btn[16], (5, 2), (1, 1), flag=layout_flag)

        # サイズ変更に追随して大きくなってほしいので指定する
        layout.AddGrowableCol(0)
        layout.AddGrowableCol(1)
        layout.AddGrowableCol(2)
        layout.AddGrowableCol(3)
        layout.AddGrowableRow(1)
        layout.AddGrowableRow(2)
        layout.AddGrowableRow(3)
        layout.AddGrowableRow(4)
        layout.AddGrowableRow(5)

        return layout

    KEYCODE_LIST = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    OPERATOR_LIST = ['+', '-', '*', '/']
    def inputnum_to_numeric(self):
        '''入力された数式をdecimal型で返す'''
        if self.input_num:
            return ''.join(self.input_num)
        else:
            return False

    def count_effective_digits(self):
        '''有効桁数を計算しておく'''
        try:
            idx = self.input_num.index('.')
        except ValueError:
            return
        rslt = len(self.input_num) - idx
        if rslt > self.effective_digit:
            self.effective_digit = rslt

    def result_copy(self):
        '''結果コピー'''
        if self.result_panel.CanCopy():
            self.result_panel.Copy()
    
    def result_all_select(self):
        '''結果全選択'''
        self.result_panel.SelectAll()

    def select_char(self, keycode, key=None):
        '''押されたキーの処理'''
        code = chr(keycode)
        if code in self.KEYCODE_LIST:
            if code == '.':
                if code not in self.input_num:
                    self.input_num.append(code)
            else:
                self.input_num.append(code)
            self.make_formula()
        elif code in self.OPERATOR_LIST:
            if self.input_num:
                self.count_effective_digits()
                self.calculation.append(self.inputnum_to_numeric())
                self.calculation.append(code)
                self.input_num = []
                self.make_formula()
        elif keycode == wx.WXK_RETURN:
            self.result_view()
        elif keycode == wx.WXK_ESCAPE:
            self.Close()
        else:
            if key:
                if key == wx.WXK_HOME:
                    self.clear_calc()
                    self.view_formula([])
                elif key == wx.WXK_CONTROL_C:
                    self.result_copy()
                elif key == wx.WXK_CONTROL_A:
                    self.result_all_select()
                # elif key == wx.WXK_CONTROL_V:
                #     # 貼り付け
                # else:
                #     print('WXK_NONE({0})'.format(key))

    def on_char(self, ev):
        '''入力をもらっておく'''
        keycode = ev.GetUnicodeKey()
        key = ev.GetKeyCode()
        self.select_char(keycode, key)

    SEND_KEYCODE = [0, '+', '-', '*', '/', '1', '2', '3', '4', '5',
        '6', '7', '8', '9', '0', 0, '.']
    def btn_press(self, ev):
        '''ボタンが押された'''
        obj = ev.GetEventObject()
        try:
            idx = self.btn.index(obj)
        except ValueError:
            pass
        else:
            # この方法はあまりよくない
            # WindowsのPostMessageみたいなのがない？
            if idx == 0:
                # CLEARコマンド
                self.clear_calc()
                self.view_formula([])
            elif idx == 15:
                # VK_RETURN
                self.select_char(wx.WXK_RETURN)
            else:
                self.select_char(ord(self.SEND_KEYCODE[idx]))
        ev.Skip()

    def make_formula_string(self, convert=True):
        '''計算式を文字列にする'''
        rslt = []
        for v in self.calculation:
            assert not isinstance(v, (int, float))
            if convert:
                if v == '/':
                    v = u'÷'
                elif v == '*':
                    v = u'×'
                elif v == '-':
                    v = u'－'
                elif v == '+':
                    v = u'＋'
            rslt.append(v)
        t = self.inputnum_to_numeric()
        if t is not False:
            rslt.append(t)
        return rslt

    def make_formula(self):
        '''表示用計算式を作成する'''
        self.view_formula(self.make_formula_string())

    def view_formula(self, v):
        '''計算式を表示する'''
        s = ''.join(v)
        if not s:
            s = '0'
        self.result_panel.SetLabel(s)
        self.result_panel.SetInsertionPointEnd()

    def result_view(self):
        '''計算結果を表示する'''
        formula = ''.join(self.make_formula_string(convert=False))
        try:
            rslt = S(formula)
        except SympifyError:
            # エラー表示
            rslt = 'ERR'
        else:
            if not rslt.is_integer:
                effective_digit = self.effective_digit
                if effective_digit == 0:
                    effective_digit = 15
                # 整数部の桁数を見る
                int_digit = len(str(int(rslt)))
                effective_digit += int_digit
                rslt = str(rslt.evalf(effective_digit)).rstrip('0').rstrip('.')
            else:
                rslt = str(rslt)
        # 結果を作る
        formula = self.make_formula_string()
        if not formula:
            return
        formula.append(u'＝')
        formula.append(rslt)
        # 表示
        self.view_formula(formula)
        # 初期化
        self.clear_calc()

    def clear_calc(self):
        '''初期化'''
        self.calculation = []
        self.input_num = []
        self.effective_digit = 0

def main():
    '''wx Calc main'''
    app = wx.App(False)
    frame = main_frame(None, title=u'wxCalc')
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
