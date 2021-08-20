' This is the macros that are in one of the Excel Model workbooks.  It contains the code for how scenarios
' are loaded and stored, among other things.  This is here for reference purposes only.


'Set Global input variables used in:
'Prepare4Public, StoreScenario, DeleteScenario_Click, LoadScenario_Click, ScrollScenario_Click
Public Const gFirstRow = 11  'First scenario record row,
Public Const gStepSize = 227 'Size (rows) of each scenario record,
Type modelVarType
    Name As String
    Value As Variant
    Mean As Variant
    Unit As String
    Low As Variant
    High As Variant
    Count As Variant 'number of entries in VMA table
    SD As Variant 'standard deviation
End Type


Sub Macr_CopyInterpolations()
'
' Macro for Data Interpolator Sheet
    'Test for complete entry
    If Range("A17").Value = "[Choose Variable]" Or _
        Range("A20").Value = "[Select Region]" Or _
        Range("A23").Value = "" Or _
        Range("A29").Value = "" Or _
        Range("A32").Value = "" Or _
        Range("G18").Value = "[Choose Fit]" Or _
        IsError(Range("G19")) Then
            MsgBox ("Required Input Missing: Please verify that all green fields are completed.")
    Else
        Application.ScreenUpdating = False
        Application.Calculation = xlManual
    
        'Set key input variables
        stepSize = 65 'rows
        firstRow = 140
        currRow = firstRow
        block = 0
        'Find empty block to store results
        Do While Not (IsEmpty(Cells(currRow, 1)))
            currRow = currRow + stepSize
            block = block + 1
        Loop
        
        'Copy and Paste Data
            ' Copy the main settings and entered data
            Range("A15:H74").Select
            Selection.Copy
            Cells(currRow, 1).Select
            Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
            SkipBlanks:=False, Transpose:=False
            
            ' Copy the Harmonized (Scaled) Data
            Range("CV18:CV73").Select
            Selection.Copy
            Cells(currRow + 4, 8).Select
            Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
            SkipBlanks:=False, Transpose:=False
        
        'Copy and Paste Formatting
        Range("A140:K199").Select
        Selection.Copy
        Cells(currRow, 1).Select
        Selection.PasteSpecial Paste:=xlPasteFormats, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
        
        'Paste Instructions
        Range("J143").Select
        Selection.Copy
        Cells(currRow, 1).Offset(3, 9).Select
        ActiveSheet.Paste
        
        Range("I144:I151").Select
        Selection.Copy
        Cells(currRow, 1).Offset(4, 8).Select
        ActiveSheet.Paste
        
        'Copy Rsquared value
        Select Case Range("G18").Value
        Case "Linear"
            rSquared = Range("AR18").Value
        Case "2nd Poly"
            rSquared = Range("AZ18").Value
        Case "3rd Poly"
            rSquared = Range("BI18").Value
        Case "Exp"
            rSquared = Range("BP18").Value
        Case "S-Curve"
            rSquared = Range("BU19").Value
        End Select
        
        'Set Record Labels
        Cells(currRow, 1).Value = block
        Cells(currRow, 1).Offset(1, 0).Value = "Variable"
        Cells(currRow, 1).Offset(4, 0).Value = "Region"
        Cells(currRow, 1).Offset(7, 0).Value = "Source"
        Cells(currRow, 1).Offset(13, 0).Value = "Base Year"
        Cells(currRow, 1).Offset(16, 0).Value = "Original Unit"
        Cells(currRow, 1).Offset(19, 0).Value = "Multiplier"
        Cells(currRow, 1).Offset(23, 0).Value = ""
        Cells(currRow, 1).Offset(1, 4).Value = ""
        Cells(currRow, 1).Offset(1, 6).Value = ""
        Cells(currRow, 1).Offset(2, 6).Value = rSquared
        Cells(currRow, 1).Offset(1, 7).Value = ""
        Cells(currRow, 1).Offset(3, 6).Value = "Trendline:" & Cells(currRow, 1).Offset(3, 6).Value
        If Cells(currRow, 1).Offset(3, 7).Value = "Yes" Then
            Cells(currRow, 1).Offset(3, 8).Value = "Raw Values Used When Avail"
        Else
            Cells(currRow, 1).Offset(3, 8).Value = "Only Trend Values Used"
        End If
        
        If Range("CY18").Value = "Yes" Then 'UN Population harmonization performed
            Cells(currRow, 1).Offset(3, 7).Value = "Fit Data Harmonized with UN Pop Data (     " & Range("CY23").Value & "->2015)"
        Else 'No UN Population harmonization performed
            Cells(currRow, 1).Offset(3, 7).Value = "No Population Harmonization Performed. Data are same as Curve Fit Data"
        End If
        
        Cells(currRow, 1).Offset(3, 9).Value = "11. NOW COPY SELECTED TRENDLINE RESULTS TO YOUR """ & Cells(currRow + 2, 1).Value & """ INPUT SHEET (only 2012 onwards)"
        Cells(currRow, 1).Offset(62, 0).Formula = "=HYPERLINK(""#""&""'""&A$1&""'!a1"",""Back to top"")"
            
        'Clear Errors in cells
        For i = 1 To 56
            If IsError(Cells(currRow + 3 + i, 6).Value) Then
                Cells(currRow, 1).Offset(3 + i, 5).Value = ""
            End If
        Next
            
        'Reset Entry Cells
        If Range("J29").Value = "Yes" Then
            Range("A17").Value = "[Choose Variable]"
            Range("A20").Value = "[Select Region]"
            Range("A23").Value = ""
            Range("A29").Value = ""
            Range("A32").Value = ""
            Range("A37").Value = ""
            Range("G18").Value = "[Choose Fit]"
            Range("H18").Value = "Yes"
            Range("E19:E74").ClearContents
        End If
        
        Application.ScreenUpdating = True
        Application.Calculation = xlAutomatic
        
        Range(Cells(currRow + 11, 8), Cells(currRow + 4, 8).Offset(55, 0)).Select
        
    End If
End Sub

Sub delete_LastInterpolation()

    Application.ScreenUpdating = False
    Application.Calculation = xlManual

    'Set major inputs and defaults
    stepSize = 65 'rows
    firstRow = 140
    currRow = firstRow
    block = 0
    'find last entered block of interpolations
    Do While Not (IsEmpty(Cells(currRow + stepSize, 1)))
        currRow = currRow + stepSize
        block = block + 1
    Loop
    'Test for saved interpolations
    If currRow > firstRow Then 'Prompt for deletion
        respo = MsgBox("Are you sure you want to delete """ & Cells(currRow, 2).Value & """?", vbYesNo)
        If respo = vbYes Then 'Delete entire rows
            Rows(currRow & ":" & currRow + stepSize).Delete
        End If
    Else 'No interpolations stored
        MsgBox ("Nothing to Delete.")
    End If
    
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
    
    Range("A15:H74").Select
End Sub

Sub ShowForm()
    If Sheets("Advanced Controls").Range("C61").Value = "" Then
        MsgBox ("Current Adoption (World) Missing. Nothing Stored.")
    Else
        If IsError(Application.Sum(Range(Sheets("Advanced Controls").Cells(277, 3), Sheets("Advanced Controls").Cells(277, 3).Offset(46, 0)).Value)) Then
            MsgBox ("Adoption is Resulting in Error, Please Check Model First. Nothing Stored")
        Else
            SaveScenarioForm.Show
        End If
    End If
End Sub

Sub StoreScenario_Click()
'
' StoreScenario_Click Macro
' Records all Inputs and Outputs of the Current Model

    
'Set key input variables
Dim currRow As Integer: currRow = gFirstRow
Dim block As Integer: block = 0
Dim HighestAdoption As Single: HighestAdoption = -2147483647
Dim HighestAdoptionName As String: HighestAdoptionName = ""
Dim HighestEmissionsRedux As Single: HighestEmissionsRedux = -2147483647
Dim HighestEmissionsReduxName As String: HighestEmissionsReduxName = ""
Dim HighestNPV As Single: HighestNPV = -2147483647
Dim HighestNPVName As String: HighestNPVName = ""
Dim HighestPPM As Single: HighestPPM = -2147483647
Dim HighestPPMName As String: HighestPPMName = ""
Dim LowestAbatementCost As Single: LowestAbatementCost = 2147483647
Dim LowestAbatementCostName As String: LowestAbatementCostName = ""
Dim Y_PDS As String: Y_PDS = ""
Dim Y_REF As String: Y_REF = ""
Dim anchor As Range
Dim num As Integer
Dim originalSheet As Worksheet
    
Application.ScreenUpdating = False
Application.Calculation = xlManual
Set originalSheet = ActiveSheet
Sheets("ScenarioRecord").Activate
'Find empty block to store results
Do While Not (IsEmpty(Cells(currRow, 1)))
    currRow = currRow + gStepSize
    block = block + 1
Loop

Range(Cells(gFirstRow, 1), Cells(gFirstRow + gStepSize - 1, 42)).Copy
With Cells(currRow, 1)
    .Select
    ActiveSheet.Paste
    
    'RESULTS -------------------------------
    'General Results Record
    Randomize
    .Value = block
    .Offset(0, 1).Value = DateTime.Now() 'keep a fixed date/time stamp record
    .Offset(4, 8).Value = Int(1000000000 * Rnd + 1) 'Generate a key, to be used for naming images for deletion later
    .Offset(0, 4).Value = SaveScenarioForm.InputBoxName
    .Offset(1, 4).Value = SaveScenarioForm.InputBoxDescription
    .Offset(2, 4).Value = CStr(Sheets("Advanced Controls").Range("H4")) + "-" + CStr(Sheets("Advanced Controls").Range("I4")) 'Analysis Period
    .Offset(2, 5).Value = Sheets("Advanced Controls").Range("C40") 'Solution Name
    Rows(currRow + 1 & ":" & currRow + 1).RowHeight = 45
    
    'Adoption
    .Offset(4, 4).Value = Sheets("Advanced Controls").Range("A4") 'Implementation Unit Increase
    .Offset(4, 5).Value = Sheets("Advanced Controls").Range("A5") 'Implementation Unit
    .Offset(5, 4).Value = Sheets("Advanced Controls").Range("A9") 'Implementation Unit Amount in Second Yr
    .Offset(5, 5).Value = Sheets("Advanced Controls").Range("A10") 'Implementation Unit
    .Offset(6, 4).Value = Sheets("Advanced Controls").Range("B4") 'Functional Unit Increase
    .Offset(6, 5).Value = Sheets("Advanced Controls").Range("B5") 'Functional Unit
    .Offset(7, 4).Value = Sheets("Advanced Controls").Range("B9") 'Functional Unit Amount in Second Yr
    .Offset(7, 5).Value = Sheets("Advanced Controls").Range("B10") 'Functional Unit
    .Offset(8, 4).Value = Sheets("Advanced Controls").Range("C9") '% Adoption - base year
    .Offset(9, 4).Value = Sheets("Advanced Controls").Range("D9") '% Adoption - Year 1
    .Offset(10, 4).Value = Sheets("Advanced Controls").Range("E9") '% Adoption - Year 2
    
    'Financial
    .Offset(16, 4).Value = Sheets("Advanced Controls").Range("C4") 'Marginal FCosts
    .Offset(17, 4).Value = Sheets("Advanced Controls").Range("D4") 'Net Ops Costs Savings
    .Offset(18, 4).Value = Sheets("Advanced Controls").Range("E4") 'Lifetime Ops Costs Savings
    .Offset(19, 4).Value = Sheets("Advanced Controls").Range("A14") 'Cumulative FCosts
    'NPV'S
    .Offset(20, 4).Value = Sheets("Advanced Controls").Range("B14") 'Single Unit Lifetime Cashflow NPV
    .Offset(21, 4).Value = Sheets("Detailed Results").Range("A50") 'All Implementation Units Lifetime Cashflow NPV
    'Profit-based NPV's
    .Offset(20, 7).Value = Sheets("Detailed Results").Range("B50") 'Single Unit Lifetime Profit Cashflow NPV
    .Offset(21, 7).Value = Sheets("Detailed Results").Range("C50") 'All Implementation Units Lifetime Profit Cashflow NPV
    
    .Offset(22, 4).Value = Sheets("Advanced Controls").Range("C14") 'Abatement Costs
    
    'NPV Payback
    .Offset(23, 4).Value = Sheets("Advanced Controls").Range("D14") 'Payback Solution v Conventional
    .Offset(24, 4).Value = Sheets("Advanced Controls").Range("E14") 'Discounted Payback Solution v Conventional
    .Offset(25, 4).Value = Sheets("Advanced Controls").Range("F14") 'Payback Solution Alone
    .Offset(26, 4).Value = Sheets("Advanced Controls").Range("G14") 'Discounted Payback Solution Alone
    'Profit-based NPV Payback
    .Offset(23, 7).Value = Sheets("Detailed Results").Range("D50") 'Profit Payback Solution v Conventional
    .Offset(24, 7).Value = Sheets("Detailed Results").Range("E50") 'Discounted Profit Payback Solution v Conventional
    .Offset(25, 7).Value = Sheets("Detailed Results").Range("F50") 'Profit Payback Solution Alone
    .Offset(26, 7).Value = Sheets("Detailed Results").Range("G50") 'Discounted Profit Payback Solution Alone
    
    'Payback Years
    .Offset(20, 5).Value = "USD, " + Sheets("Advanced Controls").Range("B16") 'Single Unit NPV
    .Offset(23, 5).Value = Sheets("Advanced Controls").Range("D16")  'Payback Solution v Conventional
    .Offset(24, 5).Value = Sheets("Advanced Controls").Range("D16")  'Discounted Payback Solution v Conventional
    .Offset(25, 5).Value = Sheets("Advanced Controls").Range("D16")  'Payback Solution Alone
    .Offset(26, 5).Value = Sheets("Advanced Controls").Range("D16")  'Discounted Payback Solution Alone
    'Profit-based Payback Years
    .Offset(20, 8).Value = "USD, " + Sheets("Detailed Results").Range("C52") 'Single Unit Profit-based NPV
    .Offset(23, 8).Value = Sheets("Detailed Results").Range("C52")   'Profit Payback Solution v Conventional
    .Offset(24, 8).Value = Sheets("Detailed Results").Range("C52")   'Discounted Profit Payback Solution v Conventional
    .Offset(25, 8).Value = Sheets("Detailed Results").Range("C52")   'Profit Payback Solution Alone
    .Offset(26, 8).Value = Sheets("Detailed Results").Range("C52")   'Discounted Profit Payback Solution Alone
    
    'Climate
    .Offset(32, 4).Value = Sheets("Advanced Controls").Range("F4") ' Total Emissions Reduction
    .Offset(33, 4).Value = Sheets("Advanced Controls").Range("A19") 'Max Annual Emissions Reduction
    .Offset(34, 4).Value = Sheets("Advanced Controls").Range("B19") 'Emissions Reduction in Year 2
    .Offset(35, 4).Value = Sheets("Advanced Controls").Range("C19") 'Approx PPM Equiv in Year 2
    .Offset(36, 4).Value = Sheets("Advanced Controls").Range("D19") 'Approx. PPM Rate of Redux in Year 2
    .Offset(37, 4).Value = Sheets("Advanced Controls").Range("E19") 'Total Direct Emissions Redux
    .Offset(38, 4).Value = Sheets("Advanced Controls").Range("F19") 'Total Indirect Emissions Redux
    .Offset(39, 4).Value = Sheets("Advanced Controls").Range("G19") 'Total Direct Energy Use Redux
    
    'FINANCIAL INPUTS -------------------------------
    'Conventional
    .Offset(47, 4).Value = sFoV(Sheets("Advanced Controls").Range("B98"), currRow) 'First Cost
    .Offset(48, 4).Value = sFoV(Sheets("Advanced Controls").Range("C98"), currRow)  'Learning Rate
    .Offset(49, 4).Value = sFoV(Sheets("Advanced Controls").Range("E98"), currRow)  'Lifetime Capacity
    .Offset(50, 4).Value = sFoV(Sheets("Advanced Controls").Range("F98"), currRow)  'Avg Annual Use
    .Offset(51, 4).Value = sFoV(Sheets("Advanced Controls").Range("H98"), currRow)  'VOM
    .Offset(52, 4).Value = sFoV(Sheets("Advanced Controls").Range("I98"), currRow)  'FOM
    .Offset(53, 4).Value = sFoV(Sheets("Advanced Controls").Range("J98"), currRow)  'Type of Fuel
    .Offset(54, 4).Value = sFoV(Sheets("Advanced Controls").Range("K98"), currRow)  'Fuel Cost
    'Units
    .Offset(47, 5).Value = Sheets("Advanced Controls").Range("B99") 'First Cost
    .Offset(49, 5).Value = Sheets("Advanced Controls").Range("E99")  'Lifetime Capacity
    .Offset(50, 5).Value = Sheets("Advanced Controls").Range("F99")  'Avg Annual Use
    .Offset(51, 5).Value = Sheets("Advanced Controls").Range("H99")  'VOM
    .Offset(52, 5).Value = Sheets("Advanced Controls").Range("I99") 'FOM
    .Offset(54, 5).Value = Sheets("Advanced Controls").Range("K97")  'Fuel Cost
    
    'Solution
    .Offset(65, 4).Value = sFoV(Sheets("Advanced Controls").Range("B113"), currRow)  'First Cost
    .Offset(66, 4).Value = sFoV(Sheets("Advanced Controls").Range("C113"), currRow)  'Learning Rate
    .Offset(66, 6).Value = sFoV(Sheets("Advanced Controls").Range("C117"), currRow)  'Cost Allowed to Drop below Conventional?
    .Offset(67, 4).Value = sFoV(Sheets("Advanced Controls").Range("E113"), currRow)  'Lifetime Capacity
    .Offset(68, 4).Value = sFoV(Sheets("Advanced Controls").Range("F113"), currRow)  'Avg Annual Use
    .Offset(69, 4).Value = sFoV(Sheets("Advanced Controls").Range("H113"), currRow)  'VOM
    .Offset(70, 4).Value = sFoV(Sheets("Advanced Controls").Range("I113"), currRow)  'FOM
    .Offset(71, 4).Value = sFoV(Sheets("Advanced Controls").Range("J113"), currRow)  'Type of Fuel
    .Offset(72, 4).Value = sFoV(Sheets("Advanced Controls").Range("K113"), currRow)  'Fuel Cost
    'Units
    .Offset(65, 5).Value = Sheets("Advanced Controls").Range("B114")  'First Cost
    .Offset(67, 5).Value = Sheets("Advanced Controls").Range("E114")  'Lifetime Capacity
    .Offset(68, 5).Value = Sheets("Advanced Controls").Range("F114") 'Avg Annual Use
    .Offset(69, 5).Value = Sheets("Advanced Controls").Range("H114") 'VOM
    .Offset(70, 5).Value = Sheets("Advanced Controls").Range("I114")  'FOM
    .Offset(72, 5).Value = Sheets("Advanced Controls").Range("K112")  'Fuel Cost
    
    'General
    .Offset(77, 4).Value = sFoV(Sheets("Advanced Controls").Range("B126"), currRow)   'Discount Rate
    
    'EMISSIONS INPUTS -------------------------------
    'Grid
    .Offset(89, 4).Value = sFoV(Sheets("Advanced Controls").Range("B144"), currRow)  'Avg Electricity CONV
    .Offset(90, 4).Value = sFoV(Sheets("Advanced Controls").Range("C144"), currRow)  'Energy efficiency Factor - SOLU
    .Offset(91, 4).Value = sFoV(Sheets("Advanced Controls").Range("D144"), currRow)  'ALTERNATIVE Energy used SOLU
    'Units
    .Offset(89, 5).Value = Sheets("Advanced Controls").Range("B143") 'Avg Electricity CONV
    .Offset(90, 5).Value = Sheets("Advanced Controls").Range("C143") 'Energy efficiency Factor - SOLU
    .Offset(91, 5).Value = Sheets("Advanced Controls").Range("D143") 'ALTERNATIVE Energy used SOLU
    
    'Fuel
    .Offset(95, 4).Value = sFoV(Sheets("Advanced Controls").Range("F144"), currRow)  'Fuel Consumed CONV
    .Offset(96, 4).Value = sFoV(Sheets("Advanced Controls").Range("G144"), currRow)  'Fuel Efficiency Factor SOLU
    .Offset(97, 4).Value = sFoV(Sheets("Advanced Controls").Range("I144"), currRow)  'Fuel Emissions Factor - Conventional
    .Offset(98, 4).Value = sFoV(Sheets("Advanced Controls").Range("I148"), currRow)  'Fuel Emissions Factor - Solution
    'Units
    .Offset(95, 5).Value = Sheets("Advanced Controls").Range("F143") 'Fuel Consumed CONV
    .Offset(97, 5).Value = Sheets("Advanced Controls").Range("H145") 'Fuel Emissions Factor Conventional
    .Offset(98, 5).Value = Sheets("Advanced Controls").Range("H149") 'Fuel Emissions Factor Solution
    
    'Direct
    .Offset(104, 4).Value = Sheets("Advanced Controls").Range("B159") 'Type of GHG
    .Offset(105, 4).Value = sFoV(Sheets("Advanced Controls").Range("C159"), currRow)  'Direct Emissions CONV
    .Offset(106, 4).Value = sFoV(Sheets("Advanced Controls").Range("D159"), currRow)  'Direct Emissions SOLU
    'Units
    .Offset(105, 5).Value = Sheets("Advanced Controls").Range("C158") 'Direct Emissions CONV
    .Offset(106, 5).Value = Sheets("Advanced Controls").Range("D158") 'Direct Emissions SOLU
    
    'Indirect
    .Offset(112, 4).Value = sFoV(Sheets("Advanced Controls").Range("F159"), currRow)  'Indirect CO2 Emissions CONV
    .Offset(113, 4).Value = sFoV(Sheets("Advanced Controls").Range("G159"), currRow)  'Indirect CO2 Emissions SOLU
    .Offset(114, 4).Value = Sheets("Advanced Controls").Range("F169") 'Implementation or Functional Unit?
    'Units
    .Offset(112, 5).Value = Sheets("Advanced Controls").Range("F158") 'Indirect CO2 Emissions CONV
    .Offset(113, 5).Value = Sheets("Advanced Controls").Range("G158") 'Indirect CO2 Emissions SOLU
            
    'Optional
    .Offset(119, 4).Value = sFoV(Sheets("Advanced Controls").Range("I159"), currRow)  'CH4 Tons Reduced
    .Offset(120, 4).Value = sFoV(Sheets("Advanced Controls").Range("J159"), currRow)  'N2O Tons Reduced
    .Offset(121, 4).Value = sFoV(Sheets("Advanced Controls").Range("I170"), currRow)  'Source for Conversion
    'Units
    .Offset(119, 5).Value = Sheets("Advanced Controls").Range("I158") 'CH4 or CH4-CO2-eq?
    .Offset(120, 5).Value = Sheets("Advanced Controls").Range("J158") 'N2O or N2O-CO2-eq?
            
    'General
    .Offset(125, 4).Value = sFoV(Sheets("Advanced Controls").Range("B174"), currRow)  'Use CO2-eq?
    .Offset(126, 4).Value = sFoV(Sheets("Advanced Controls").Range("C174"), currRow)  'Source
    .Offset(127, 4).Value = sFoV(Sheets("Advanced Controls").Range("D174"), currRow)  'Range
    
    'TAM -------------------------------
    'Source
    .Offset(136, 4).Value = Sheets("Advanced Controls").Range("B53") ' Source - Current
    .Offset(136, 7).Value = Sheets("Advanced Controls").Range("B54") ' Source - Future REF
    .Offset(136, 10).Value = Sheets("Advanced Controls").Range("B55") ' Source - Future PDS
    
    'Values
    .Offset(137, 4).Value = Sheets("Advanced Controls").Range("F53") ' Value - Current
    .Offset(137, 7).Value = Sheets("Advanced Controls").Range("F54") ' Value - Future REF
    .Offset(137, 10).Value = Sheets("Advanced Controls").Range("F55") ' Value - Future PDS
    
    'Units
    .Offset(137, 5).Value = Sheets("Advanced Controls").Range("G53") ' TAM - Current
    .Offset(137, 8).Value = Sheets("Advanced Controls").Range("G55") ' TAM - Future REF
    .Offset(137, 11).Value = Sheets("Advanced Controls").Range("G54") ' TAM - Future PDS
    
    'ADOPTION -------------------------------
    .Offset(151, 4).Value = sFoV(Sheets("Advanced Controls").Range("C61"), currRow) 'World
    .Offset(152, 4).Value = sFoV(Sheets("Advanced Controls").Range("C62"), currRow) 'OECD90
    .Offset(153, 4).Value = sFoV(Sheets("Advanced Controls").Range("C63"), currRow) 'EE
    .Offset(154, 4).Value = sFoV(Sheets("Advanced Controls").Range("C64"), currRow) 'Asia
    .Offset(155, 4).Value = sFoV(Sheets("Advanced Controls").Range("C65"), currRow) 'MEA
    .Offset(156, 4).Value = sFoV(Sheets("Advanced Controls").Range("C66"), currRow) 'LaTam
    .Offset(157, 4).Value = sFoV(Sheets("Advanced Controls").Range("C67"), currRow) 'China
    .Offset(158, 4).Value = sFoV(Sheets("Advanced Controls").Range("C68"), currRow) 'India
    .Offset(159, 4).Value = sFoV(Sheets("Advanced Controls").Range("C69"), currRow) 'EU27
    .Offset(160, 4).Value = sFoV(Sheets("Advanced Controls").Range("C70"), currRow) 'USA
    'Units
    .Offset(151, 5).Value = Sheets("Advanced Controls").Range("D61") 'World
    .Offset(152, 5).Value = Sheets("Advanced Controls").Range("D62") 'OECD90
    .Offset(153, 5).Value = Sheets("Advanced Controls").Range("D63") 'EE
    .Offset(154, 5).Value = Sheets("Advanced Controls").Range("D64") 'Asia
    .Offset(155, 5).Value = Sheets("Advanced Controls").Range("D65") 'MEA
    .Offset(156, 5).Value = Sheets("Advanced Controls").Range("D66") 'LaTam
    .Offset(157, 5).Value = Sheets("Advanced Controls").Range("D67") 'China
    .Offset(158, 5).Value = Sheets("Advanced Controls").Range("D68") 'India
    .Offset(159, 5).Value = Sheets("Advanced Controls").Range("D69") 'EU27
    .Offset(160, 5).Value = Sheets("Advanced Controls").Range("D70") 'USA
    
    'PDS ADOPTION SCENARIO INPUTS  ----------------------------------
    .Offset(164, 4).Value = sFoV(Sheets("Advanced Controls").Range("B228"), currRow) 'Base Custom Adoption on
    .Offset(165, 4).Value = sFoV(Sheets("Advanced Controls").Range("B231"), currRow) 'Regional Data Only?
    
    Select Case .Offset(164, 4).Value
    Case "DEFAULT Linear", "DEFAULT S-Curve"
        'Linear and S-Curve
        .Offset(170, 4).Value = sFoV(Sheets("Advanced Controls").Range("E238"), currRow)
        .Offset(171, 4).Value = sFoV(Sheets("Advanced Controls").Range("E239"), currRow)
        .Offset(172, 4).Value = sFoV(Sheets("Advanced Controls").Range("E240"), currRow)
        .Offset(173, 4).Value = sFoV(Sheets("Advanced Controls").Range("E241"), currRow)
        .Offset(174, 4).Value = sFoV(Sheets("Advanced Controls").Range("E242"), currRow)
        .Offset(175, 4).Value = sFoV(Sheets("Advanced Controls").Range("E243"), currRow)
        .Offset(176, 4).Value = sFoV(Sheets("Advanced Controls").Range("E244"), currRow)
        .Offset(177, 4).Value = sFoV(Sheets("Advanced Controls").Range("E245"), currRow)
        .Offset(178, 4).Value = sFoV(Sheets("Advanced Controls").Range("E246"), currRow)
        .Offset(179, 4).Value = sFoV(Sheets("Advanced Controls").Range("E247"), currRow)
    
        If Sheets("S-Curve Adoption").Range("J13").Value = "This Model" Then
            .Offset(181, 4).Value = "Default S-Curve (Logistic Model)"
        Else
            .Offset(181, 4).Value = "Alternate S-Curve (Bass Model)"
        
            'Bass Diffusion Model numbers - Innovation Parameter
            .Offset(170, 6).Value = sFoV(Sheets("Advanced Controls").Range("J238"), currRow) 'World
            .Offset(171, 6).Value = sFoV(Sheets("Advanced Controls").Range("J239"), currRow) 'OECD90
            .Offset(172, 6).Value = sFoV(Sheets("Advanced Controls").Range("J240"), currRow) 'Eastern Europe
            .Offset(173, 6).Value = sFoV(Sheets("Advanced Controls").Range("J241"), currRow) 'Asia SJapan
            .Offset(174, 6).Value = sFoV(Sheets("Advanced Controls").Range("J242"), currRow) 'Middle East + Africa
            .Offset(175, 6).Value = sFoV(Sheets("Advanced Controls").Range("J243"), currRow) 'Latam
            .Offset(176, 6).Value = sFoV(Sheets("Advanced Controls").Range("J244"), currRow) 'China
            .Offset(177, 6).Value = sFoV(Sheets("Advanced Controls").Range("J245"), currRow) 'India
            .Offset(178, 6).Value = sFoV(Sheets("Advanced Controls").Range("J246"), currRow) 'EU
            .Offset(179, 6).Value = sFoV(Sheets("Advanced Controls").Range("J247"), currRow) 'USA
            
            'Bass Diffusion Model numbers - Imitation Parameter
            .Offset(170, 7).Value = sFoV(Sheets("Advanced Controls").Range("K238"), currRow) 'World
            .Offset(171, 7).Value = sFoV(Sheets("Advanced Controls").Range("K239"), currRow) 'OECD90
            .Offset(172, 7).Value = sFoV(Sheets("Advanced Controls").Range("K240"), currRow) 'Eastern Europe
            .Offset(173, 7).Value = sFoV(Sheets("Advanced Controls").Range("K241"), currRow) 'Asia SJapan
            .Offset(174, 7).Value = sFoV(Sheets("Advanced Controls").Range("K242"), currRow) 'Middle East + Africa
            .Offset(175, 7).Value = sFoV(Sheets("Advanced Controls").Range("K243"), currRow) 'Latam
            .Offset(176, 7).Value = sFoV(Sheets("Advanced Controls").Range("K244"), currRow) 'China
            .Offset(177, 7).Value = sFoV(Sheets("Advanced Controls").Range("K245"), currRow) 'India
            .Offset(178, 7).Value = sFoV(Sheets("Advanced Controls").Range("K246"), currRow) 'EU
            .Offset(179, 7).Value = sFoV(Sheets("Advanced Controls").Range("K247"), currRow) 'USA
        End If
        
    Case "Existing Adoption Prognostications"
        'Existing Prognostications
        .Offset(184, 4).Value = sFoV(Sheets("Advanced Controls").Range("B250"), currRow)
        .Offset(185, 4).Value = sFoV(Sheets("Advanced Controls").Range("B255"), currRow)
        .Offset(186, 4).Value = sFoV(Sheets("Advanced Controls").Range("C255"), currRow)
        
    Case "Customized S-Curve Adoption"
        'Customized S-Curve
        .Offset(190, 4).Value = sFoV(Sheets("Advanced Controls").Range("E251"), currRow)
        .Offset(191, 4).Value = sFoV(Sheets("Advanced Controls").Range("E254"), currRow)
        
    Case "Fully Customized PDS"
        'Fully Customized PDS
        .Offset(195, 4).Value = sFoV(Sheets("Advanced Controls").Range("H250"), currRow)
    End Select
    
    'REF ADOPTION SCENARIO INPUTS ------------------------------
    .Offset(199, 4).Value = sFoV(Sheets("Advanced Controls").Range("B264"), currRow) 'REF Adoption Scenario Type
    If .Offset(199, 4).Value <> "Default" Then
        .Offset(200, 4).Value = sFoV(Sheets("Advanced Controls").Range("B267"), currRow) 'Custom REF Adoption Scenario
    End If
    .Offset(201, 4).Value = sFoV(Sheets("Advanced Controls").Range("B269"), currRow) 'Use Regional Only?
    
    'ADDITIONAL VARIABLES ----------------------------
    
    If Sheets("Advanced Controls").Range("B192").Value <> "" Then
        .Offset(207, 4).Value = sFoV(Sheets("Advanced Controls").Range("B192"), currRow)
        .Offset(207, 5).Value = Sheets("Advanced Controls").Range("B193").Value 'Units
        .Offset(207, 3).Value = Sheets("Advanced Controls").Range("B190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("C192").Value <> "" Then
        .Offset(208, 4).Value = sFoV(Sheets("Advanced Controls").Range("C192"), currRow)
        .Offset(208, 5).Value = Sheets("Advanced Controls").Range("C193").Value 'Units
        .Offset(208, 3).Value = Sheets("Advanced Controls").Range("C190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("D192").Value <> "" Then
        .Offset(209, 4).Value = sFoV(Sheets("Advanced Controls").Range("D192"), currRow)
        .Offset(209, 5).Value = Sheets("Advanced Controls").Range("D193").Value 'Units
        .Offset(209, 3).Value = Sheets("Advanced Controls").Range("D190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("E192").Value <> "" Then
        .Offset(210, 4).Value = sFoV(Sheets("Advanced Controls").Range("E192"), currRow)
        .Offset(210, 5).Value = Sheets("Advanced Controls").Range("E193").Value 'Units
        .Offset(210, 3).Value = Sheets("Advanced Controls").Range("E190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("F192").Value <> "" Then
        .Offset(211, 4).Value = sFoV(Sheets("Advanced Controls").Range("F192"), currRow)
        .Offset(211, 5).Value = Sheets("Advanced Controls").Range("F193").Value 'Units
        .Offset(211, 3).Value = Sheets("Advanced Controls").Range("F190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("G192").Value <> "" Then
        .Offset(212, 4).Value = sFoV(Sheets("Advanced Controls").Range("G192"), currRow)
        .Offset(212, 5).Value = Sheets("Advanced Controls").Range("G193").Value 'Units
        .Offset(212, 3).Value = Sheets("Advanced Controls").Range("G190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("H192").Value <> "" Then
        .Offset(213, 4).Value = sFoV(Sheets("Advanced Controls").Range("H192"), currRow)
        .Offset(213, 5).Value = Sheets("Advanced Controls").Range("H193").Value 'Units
        .Offset(213, 3).Value = Sheets("Advanced Controls").Range("H190").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("B207").Value <> "" Then
        .Offset(207, 8).Value = sFoV(Sheets("Advanced Controls").Range("B207"), currRow)
        .Offset(207, 9).Value = Sheets("Advanced Controls").Range("B208").Value 'Units
        .Offset(207, 7).Value = Sheets("Advanced Controls").Range("B205").Value 'Name
    End If
     
    If Sheets("Advanced Controls").Range("C207").Value <> "" Then
        .Offset(208, 8).Value = sFoV(Sheets("Advanced Controls").Range("C207"), currRow)
        .Offset(208, 9).Value = Sheets("Advanced Controls").Range("C208").Value 'Units
        .Offset(208, 7).Value = Sheets("Advanced Controls").Range("C205").Value 'Name
    End If
     
    If Sheets("Advanced Controls").Range("D207").Value <> "" Then
        .Offset(209, 8).Value = sFoV(Sheets("Advanced Controls").Range("D207"), currRow)
        .Offset(209, 9).Value = Sheets("Advanced Controls").Range("D208").Value 'Units
        .Offset(209, 7).Value = Sheets("Advanced Controls").Range("D205").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("E207").Value <> "" Then
        .Offset(210, 8).Value = sFoV(Sheets("Advanced Controls").Range("E207"), currRow)
        .Offset(210, 9).Value = Sheets("Advanced Controls").Range("E208").Value 'Units
        .Offset(210, 7).Value = Sheets("Advanced Controls").Range("E205").Value 'Name
    End If
     
    If Sheets("Advanced Controls").Range("F207").Value <> "" Then
        .Offset(211, 8).Value = sFoV(Sheets("Advanced Controls").Range("F207"), currRow)
        .Offset(211, 9).Value = Sheets("Advanced Controls").Range("F208").Value 'Units
        .Offset(211, 7).Value = Sheets("Advanced Controls").Range("F205").Value 'Name
    End If
    
    If Sheets("Advanced Controls").Range("G207").Value <> "" Then
        .Offset(212, 8).Value = sFoV(Sheets("Advanced Controls").Range("G207"), currRow)
        .Offset(212, 9).Value = Sheets("Advanced Controls").Range("G208").Value 'Units
        .Offset(212, 7).Value = Sheets("Advanced Controls").Range("G205").Value 'Name
    End If
     
    If Sheets("Advanced Controls").Range("H207").Value <> "" Then
        .Offset(213, 8).Value = sFoV(Sheets("Advanced Controls").Range("H207"), currRow)
        .Offset(213, 9).Value = Sheets("Advanced Controls").Range("H208").Value 'Units
        .Offset(213, 7).Value = Sheets("Advanced Controls").Range("H205").Value 'Name
    End If
                  
    'Adoption Adjustment
    For yr = 2014 To 2060
        If Sheets("Advanced Controls").Cells(yr - 1737, 6).Value = "Y-PDS" Then
            Y_PDS = Y_PDS + CStr(yr) + ","
        ElseIf Sheets("Advanced Controls").Cells(yr - 1737, 6).Value = "Y-REF" Then
            Y_REF = Y_REF + CStr(yr) + ","
        End If
    Next
    If Y_PDS <> "" Then
        .Offset(218, 4).Value = Y_PDS
    Else
        .Offset(218, 4).Value = "(none)"
    End If
    If Y_REF <> "" Then
        .Offset(219, 4).Value = Y_REF
    Else
        .Offset(219, 4).Value = "(none)"
    End If
            
    'GLOBAL ANNUAL VALUES ---------------------------------------
    
    'TAM-REF
    Sheets("Unit Adoption Calculations").Range("B17:B63").Copy
    .Offset(6, 18).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    .Offset(3, 18).Value = Sheets("Advanced Controls").Range("C41").Value
    
    'TAM-PDS
    Sheets("Unit Adoption Calculations").Range("B69:B115").Copy
    .Offset(6, 19).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    .Offset(3, 19).Value = Sheets("Advanced Controls").Range("C41").Value
    
    'Adoption-REF
    Sheets("Helper Tables").Range("C27:C73").Copy
    .Offset(6, 20).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    .Offset(3, 20).Value = Sheets("Advanced Controls").Range("C41").Value
    
    'Adoption-PDS
    Sheets("Helper Tables").Range("C91:C137").Copy
    .Offset(6, 21).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    .Offset(3, 21).Value = Sheets("Advanced Controls").Range("C41").Value
    
    'OPS-REF
    Sheets("Operating Cost").Range("C69:C114").Copy
    .Offset(7, 22).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    
    'OPS-PDS
    Sheets("Operating Cost").Range("B69:B114").Copy
    .Offset(7, 23).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    
    'Emission Reduction
    Sheets("CO2 Calcs").Range("M65:M110").Copy
    .Offset(7, 24).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    
    'PPMReduction
    Sheets("CO2 Calcs").Range("B172:B217").Copy
    .Offset(7, 25).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    
    'Abatement Cost Table
    Sheets("Detailed Results").Range("P41:P141").Copy
    .Offset(4, 32).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
        
    'IMAGES -----------------------------------
    Sheets("Detailed Results").Activate 'Ensures the Payback Graph is most up to date
    Application.Calculation = xlManual
    Application.ScreenUpdating = False
    Application.EnableEvents = False 'Disable events, especially the Activate Code for Detailed Results
    
    Sheets("Detailed Results").ChartObjects("ChartWorldAdoption").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(4, 8)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-1"
    
    Sheets("Detailed Results").ChartObjects("ChartRegionalAdoption").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(4, 13)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-2"
    
    Sheets("Detailed Results").ChartObjects("ChartYoYGrowth").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(17, 8)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-3"

    Sheets("Detailed Results").ChartObjects("ChartNetSavings").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(17, 13)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-4"
    
    Sheets("Detailed Results").ChartObjects("ChartGTCO2Cumu").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(30, 8)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-5"

    Sheets("Detailed Results").ChartObjects("ChartPPMCO2").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(30, 13)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-6"

    Sheets("Detailed Results").ChartObjects("ChartAbatement").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(43, 8)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-7"

    Sheets("Detailed Results").ChartObjects("ChartPayback").Activate
    ActiveChart.ChartArea.Copy
    Sheets("ScenarioRecord").Activate
    Range(.Offset(0, 9), .Offset(0, 13)).Select
    Sheets("ScenarioRecord").Pictures.Paste.Select
    Set anchor = .Offset(43, 13)
    Selection.ShapeRange.LockAspectRatio = msoFalse
    Selection.ShapeRange.Height = 160
    Selection.ShapeRange.Width = 230
    Selection.ShapeRange.Left = anchor.Left
    Selection.ShapeRange.Top = anchor.Top
    Selection.Name = "Chart-" + CStr(.Offset(4, 8).Value) + "-8"
      
    Application.EnableEvents = True 'Enable events, especially the Activate Code for Detailed Results
    
    'FINALIZE -----------------------------------
    'Store scenario count
    Cells(1, 4).Value = block
    
    'record name in Dropdown box list
    Range("AR12").Offset(block, 0).Value = SaveScenarioForm.InputBoxName
    
    'Get Scenario Statistics
    For num = gFirstRow + gStepSize To (gFirstRow + block * gStepSize) Step gStepSize
        If Cells(num + 4, 5).Value <> "-" And Cells(num + 4, 5).Value > HighestAdoption Then
            HighestAdoption = Cells(num + 4, 5).Value
            HighestAdoptionName = Cells(num, 5)
        End If
        If Cells(num + 20, 5).Value <> "-" And Cells(num + 20, 5).Value > HighestNPV Then
            HighestNPV = Cells(num + 20, 5).Value
            HighestNPVName = Cells(num, 5)
        End If
        If Cells(num + 32, 5).Value <> "-" And Cells(num + 32, 5).Value > HighestEmissionsRedux Then
            HighestEmissionsRedux = Cells(num + 32, 5).Value
            HighestEmissionsReduxName = Cells(num, 5)
        End If
        If Cells(num + 36, 5).Value <> "-" And Cells(num + 36, 5).Value > HighestPPM Then
            HighestPPM = Cells(num + 36, 5).Value
            HighestPPMName = Cells(num, 5)
        End If
        If Cells(num + 22, 5).Value <> "-" And Cells(num + 22, 5).Value < LowestAbatementCost Then
            LowestAbatementCost = Cells(num + 22, 5).Value
            LowestAbatementCostName = Cells(num, 5)
        End If
    Next
    
    Cells(3, 4).Value = HighestAdoptionName
    Cells(4, 4).Value = HighestNPVName
    Cells(5, 4).Value = HighestEmissionsReduxName
    Cells(6, 4).Value = HighestPPMName
    Cells(7, 4).Value = LowestAbatementCostName
    
    'Highlight scenario results
    Range(.Offset(0, 1), .Offset(40, 6)).Select
    ActiveWindow.ScrollRow = .Offset(0, 0).Row
    
    If Sheets("ScenarioRecord").Visible = False Then
        originalSheet.Activate
    End If
End With
    
Application.ScreenUpdating = True
Application.Calculation = xlAutomatic
        
End Sub

Sub DeleteScenario_Click()
'
' Identifies and Deletes the record from this sheet

If Sheets("ScenarioRecord").Range("B9").Value <> "" Then
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("ScenarioRecord").Activate
    
    'Set key input variables
    Dim currRow As Integer: currRow = gFirstRow
    Dim block As Integer: block = 0
    Dim HighestAdoption As Single: HighestAdoption = -2147483647
    Dim HighestAdoptionName As String: HighestAdoptionName = ""
    Dim HighestEmissionsRedux As Single: HighestEmissionsRedux = -2147483647
    Dim HighestEmissionsReduxName As String: HighestEmissionsReduxName = ""
    Dim HighestNPV As Single: HighestNPV = -2147483647
    Dim HighestNPVName As String: HighestNPVName = ""
    Dim HighestPPM As Single: HighestPPM = -2147483647
    Dim HighestPPMName As String: HighestPPMName = ""
    Dim LowestAbatementCost As Single: LowestAbatementCost = 2147483647
    Dim LowestAbatementCostName As String: LowestAbatementCostName = ""
    Dim Name As String: Name = Range("B9").Value
    Dim respo As Integer
    Dim stamp As Long
    Dim num As Integer
    
    'Find block of selected scenario
    Do While Not Name = Cells(currRow, 5).Value And currRow < 10 + gStepSize * (1 + Range("D1").Value)  'Prevent searching for nonexistent scenarios
        currRow = currRow + gStepSize
        block = block + 1
    Loop
    
    If currRow < 10 + gStepSize * (1 + Range("D1").Value) Then 'match found
        respo = MsgBox("Are you sure you want to delete """ & Name & """?", vbYesNo, "Delete Scenario")
        If respo = vbYes Then 'Delete
            'Get Date/Time stamp
            stamp = Cells(currRow, 1).Offset(4, 8).Value
            'Delete Images first
            For num = 1 To 8
                ActiveSheet.Pictures("Chart-" + CStr(stamp) + "-" + CStr(num)).Delete
            Next
            'Delete record
            Rows(currRow & ":" & currRow + gStepSize - 1).Delete
            
            'Renumber remaining records, get scenario statistics
            currRow = gFirstRow
            num = 0
            Cells(currRow, 1).Value = num
            Do While Not (IsEmpty(Cells(currRow + gStepSize, 5)))
                currRow = currRow + gStepSize
                num = num + 1
                Cells(currRow, 1).Value = num
                
                If Cells(currRow + 4, 5).Value <> "-" And Cells(currRow + 4, 5).Value > HighestAdoption Then
                    HighestAdoption = Cells(currRow + 4, 5).Value
                    HighestAdoptionName = Cells(currRow, 5)
                End If
                If Cells(currRow + 20, 5).Value <> "-" And Cells(currRow + 20, 5).Value > HighestNPV Then
                    HighestNPV = Cells(currRow + 20, 5).Value
                    HighestNPVName = Cells(currRow, 5)
                End If
                If Cells(currRow + 32, 5).Value <> "-" And Cells(currRow + 32, 5).Value > HighestEmissionsRedux Then
                    HighestEmissionsRedux = Cells(currRow + 32, 5).Value
                    HighestEmissionsReduxName = Cells(currRow, 5)
                End If
                If Cells(currRow + 36, 5).Value <> "-" And Cells(currRow + 36, 5).Value > HighestPPM Then
                    HighestPPM = Cells(currRow + 36, 5).Value
                    HighestPPMName = Cells(currRow, 5)
                End If
                If Cells(currRow + 22, 5).Value <> "-" And Cells(currRow + 22, 5).Value < LowestAbatementCost Then
                    LowestAbatementCost = Cells(currRow + 22, 5).Value
                    LowestAbatementCostName = Cells(currRow, 5)
                End If
            Loop
            Cells(3, 4).Value = HighestAdoptionName
            Cells(4, 4).Value = HighestNPVName
            Cells(5, 4).Value = HighestEmissionsReduxName
            Cells(6, 4).Value = HighestPPMName
            Cells(7, 4).Value = LowestAbatementCostName
            
            'Delete Name from Name list, shift remaining records
            Range(Cells(12 + block + 1, 44), Cells(92, 44)).Select
            Selection.Copy
            Cells(12 + block, 44).Select
            Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, _
            SkipBlanks:=False, Transpose:=False
            
            Range("B9").Value = "" 'Reset selection cell
            Range("D1").Value = num  'Store Scenario Count
            ActiveWindow.ScrollRow = Cells(currRow, 1).Row
            
        End If
    Else
        MsgBox ("Scenario Not Found!, Nothing Deleted.")
        Range("B9").Value = ""
    End If
        
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
Else
    MsgBox ("Please Select a Scenario in Green Cell B9 of ScenarioRecord")
End If
End Sub

Sub ScrollScenario_Click()
'
' scrolls screen to a particular scenario

If Sheets("ScenarioRecord").Range("B9").Value <> "" Then
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("ScenarioRecord").Activate
    
    'Set key input variables
    Dim currRow As Integer: currRow = gFirstRow
    Dim block As Integer: block = 0
    Dim Name As String: Name = Range("B9").Value
    
    'Find block of selected scenario
    Do While Not Name = Cells(currRow, 5).Value And currRow < 10 + gStepSize * (1 + Range("D1").Value)  'Prevent searching for nonexistent scenarios
        currRow = currRow + gStepSize
        block = block + 1
    Loop
    
    If currRow < 10 + gStepSize * (1 + Range("D1").Value) Then  'match found
            ActiveWindow.ScrollRow = Cells(currRow, 1).Row
    Else
        MsgBox ("Scenario Not Found!")
        Range("B9").Value = ""
    End If
        
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
Else
    MsgBox ("Please Select a Scenario in Green Cell B9 of ScenarioRecord")
End If

End Sub


Sub LoadScenario_Click(Optional calledDirectly As Boolean = True)
'
' Loads The Inputs of a particular scenario into the Model (ie deletes current inputs)

If Sheets("ScenarioRecord").Range("B9").Value <> "" Then
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("ScenarioRecord").Activate
    
    'Set key input variables
    Dim currRow As Integer: currRow = gFirstRow
    Dim block As Integer: block = 0
    Dim alwaysValues As Boolean: alwaysValues = False
    Dim Name As String: Name = Range("B9").Value
    Dim respo As Integer
    Dim excellangID As Integer
    Dim excelLang As String
    Dim sceLang As String
    Dim XLLang As Range: Set XLLang = Sheets("XLLang").Range("XLLangs")
    Dim Y_PDS As Variant: Y_PDS = ["1","2","3"]
    Dim Y_REF As Variant: Y_REF = ["1","2","3"]
    
    'Sheets("XLLang").Visible = xlVeryHidden
    
    'Find block of selected scenario
    Do While Not Name = Cells(currRow, 5).Value And currRow < 10 + gStepSize * (1 + Range("D1").Value) 'Prevent searching for nonexistent scenarios
        currRow = currRow + gStepSize
        block = block + 1
    Loop
    
    If currRow < 10 + gStepSize * (1 + Range("D1").Value) Then 'match found
        respo = MsgBox("Are you sure you want to load """ & Name & """ into model?" & Chr(10) & "WARNINGS: " & Chr(10) & "1.MODEL INPUTS WILL BE DELETED!" & Chr(10) & "Possibly Deleted Inputs: Conventional and Solution Costs, Emissions, TAM and Adoption Sources, Adoption Scenarios, Analysis Years." & Chr(10) & Chr(10) & "2. UNITS OF MODEL ASSUMED TO BE UNITS OF SCENARIO RECORD. PLEASE VERIFY.", vbYesNo + vbExclamation, "Load Scenario")
        If respo = vbYes Then 'load data
            With Cells(currRow, 1)
                Sheets("Advanced Controls").Range("H4").Value = Left(.Offset(2, 4).Value, 4)
                Sheets("Advanced Controls").Range("I4").Value = Right(.Offset(2, 4).Value, 4)
                                
                'Test for formulae language
                'Test the conditional compiler constant #Mac
                #If Mac Then ' Mac
                    excellangID = Application.LocalizedLanguage
                #Else ' Windows
                    excellangID = Application.LanguageSettings.LanguageID(msoLanguageIDUI)
                #End If
                If .Offset(4, 13).Value <> "" Then
                    excelLang = Application.WorksheetFunction.VLookup(excellangID, XLLang, 2, False)
                    sceLang = Application.WorksheetFunction.VLookup(.Offset(4, 13), XLLang, 2, False)
                
                    If Not (StrComp(excelLang, sceLang, vbTextCompare) = 0) Then
                        respo = MsgBox("The Language of the Excel formulae stored in this Scenario differ to that of your current Excel " & _
                        "instance, so errors may result. The Language of the Scenario is " & sceLang & ", but your Excel is using " & excelLang & _
                            ". " & Chr(10) & Chr(10) & "Instead of the formulae, would You like to load only the values?", vbYesNo)
                        If respo = vbYes Then
                            alwaysValues = True
                        End If
                    End If
                End If
                
                'FINANCIAL INPUTS -------------------------------
                'Conventional
                Sheets("Advanced Controls").Range("B98") = lFoV(.Offset(47, 4).Value, alwaysValues) 'First Cost
                Sheets("Advanced Controls").Range("C98") = lFoV(.Offset(48, 4).Value, alwaysValues) 'Learning Rate
                Sheets("Advanced Controls").Range("E98") = lFoV(.Offset(49, 4).Value, alwaysValues) 'Lifetime Capacity
                Sheets("Advanced Controls").Range("F98") = lFoV(.Offset(50, 4).Value, alwaysValues) 'Avg Annual Use
                Sheets("Advanced Controls").Range("H98") = lFoV(.Offset(51, 4).Value, alwaysValues) 'VOM
                Sheets("Advanced Controls").Range("I98") = lFoV(.Offset(52, 4).Value, alwaysValues) 'FOM
                Sheets("Advanced Controls").Range("J98") = lFoV(.Offset(53, 4).Value, alwaysValues) 'Type of Fuel
                Sheets("Advanced Controls").Range("K98") = lFoV(.Offset(54, 4).Value, alwaysValues) 'Fuel Cost
    
                'Solution
                Sheets("Advanced Controls").Range("B113") = lFoV(.Offset(65, 4).Value, alwaysValues) 'First Cost
                Sheets("Advanced Controls").Range("C113") = lFoV(.Offset(66, 4).Value, alwaysValues) 'Learning Rate
                Sheets("Advanced Controls").Range("C117") = lFoV(.Offset(66, 6).Value, alwaysValues) 'Cost Allowed Below Conventional
                Sheets("Advanced Controls").Range("E113") = lFoV(.Offset(67, 4).Value, alwaysValues) 'Lifetime Capacity
                Sheets("Advanced Controls").Range("F113") = lFoV(.Offset(68, 4).Value, alwaysValues) 'Avg Annual Use
                Sheets("Advanced Controls").Range("H113") = lFoV(.Offset(69, 4).Value, alwaysValues) 'VOM
                Sheets("Advanced Controls").Range("I113") = lFoV(.Offset(70, 4).Value, alwaysValues) 'FOM
                Sheets("Advanced Controls").Range("J113") = lFoV(.Offset(71, 4).Value, alwaysValues) 'Type of Fuel
                Sheets("Advanced Controls").Range("K113") = lFoV(.Offset(72, 4).Value, alwaysValues) 'Fuel Cost
                
                'General
                Sheets("Advanced Controls").Range("B126") = lFoV(.Offset(77, 4).Value, alwaysValues) 'Disc Rate
                
                'EMISSIONS INPUTS -------------------------------
                'Grid
                Sheets("Advanced Controls").Range("B144") = lFoV(.Offset(89, 4).Value, alwaysValues) 'Avg Electricity CONV
                Sheets("Advanced Controls").Range("C144") = lFoV(.Offset(90, 4).Value, alwaysValues) 'Energy efficiency Factor - SOLU
                Sheets("Advanced Controls").Range("D144") = lFoV(.Offset(91, 4).Value, alwaysValues) 'ALTERNATIVE Energy used SOLU
                
                'Fuel
                Sheets("Advanced Controls").Range("F144") = lFoV(.Offset(95, 4).Value, alwaysValues) 'Fuel Consumed CONV
                Sheets("Advanced Controls").Range("G144") = lFoV(.Offset(96, 4).Value, alwaysValues) 'Fuel Efficiency Factor SOLU
                Sheets("Advanced Controls").Range("I144") = lFoV(.Offset(97, 4).Value, alwaysValues) 'Fuel Emissions Factor - Conventional
                Sheets("Advanced Controls").Range("I148") = lFoV(.Offset(98, 4).Value, alwaysValues) 'Fuel Emissions Factor - Solution
                
                'Direct
                Sheets("Advanced Controls").Range("B159") = .Offset(104, 4).Value 'Type of GHG
                Sheets("Advanced Controls").Range("C159") = lFoV(.Offset(105, 4).Value, alwaysValues) 'Direct Emissions CONV
                Sheets("Advanced Controls").Range("D159") = lFoV(.Offset(106, 4).Value, alwaysValues) 'Direct Emissions SOLU
                
                'Indirect
                Sheets("Advanced Controls").Range("F159") = lFoV(.Offset(112, 4).Value, alwaysValues) 'Indirect CO2 Emissions CONV
                Sheets("Advanced Controls").Range("G159") = lFoV(.Offset(113, 4).Value, alwaysValues) 'Indirect CO2 Emissions SOLU
                Sheets("Advanced Controls").Range("F169").Value = .Offset(114, 4).Value 'Functional or Implementation Units?
                
                'Optional Emissions
                Sheets("Advanced Controls").Range("I159") = lFoV(.Offset(119, 4).Value, alwaysValues) 'CH4 Tons Reduced
                If (.Offset(119, 5).Value = "t CH4 per Functional Unit") Then
                    Sheets("Advanced Controls").Range("I169").Value = "CH4"
                Else
                    Sheets("Advanced Controls").Range("I169").Value = "CH4-CO2eq"
                End If
                
                Sheets("Advanced Controls").Range("J159") = lFoV(.Offset(120, 4).Value, alwaysValues) 'N2O Tons Reduced
                If (.Offset(120, 5).Value = "t N2O per Functional Unit") Then
                    Sheets("Advanced Controls").Range("J169").Value = "N2O"
                Else
                    Sheets("Advanced Controls").Range("J169").Value = "N2O-CO2eq"
                End If
                
                Sheets("Advanced Controls").Range("I170") = lFoV(.Offset(121, 4).Value, alwaysValues) 'Source for CO2 Conversion
                
                'General
                Sheets("Advanced Controls").Range("B174") = lFoV(.Offset(125, 4).Value, alwaysValues) 'Use CO2-eq?
                Sheets("Advanced Controls").Range("C174") = lFoV(.Offset(126, 4).Value, alwaysValues) 'Source
                Sheets("Advanced Controls").Range("D174") = lFoV(.Offset(127, 4).Value, alwaysValues) 'Range
                
                'TAM -------------------------------
                'Sources
                Sheets("Advanced Controls").Range("B53") = lFoV(.Offset(136, 4).Value, alwaysValues) ' - Current
                Sheets("Advanced Controls").Range("B54") = lFoV(.Offset(136, 7).Value, alwaysValues) ' - REF TAM
                Sheets("Advanced Controls").Range("B55") = lFoV(.Offset(136, 10).Value, alwaysValues) ' - PDS TAM
                
                'ADOPTION SCENARIO INPUTS -------------------------------
                
                'Current Adoption
                Sheets("Advanced Controls").Range("C61") = lFoV(.Offset(151, 4).Value, alwaysValues) 'World
                Sheets("Advanced Controls").Range("C62") = lFoV(.Offset(152, 4).Value, alwaysValues) 'OECD90
                Sheets("Advanced Controls").Range("C63") = lFoV(.Offset(153, 4).Value, alwaysValues) 'EE
                Sheets("Advanced Controls").Range("C64") = lFoV(.Offset(154, 4).Value, alwaysValues) 'Asia
                Sheets("Advanced Controls").Range("C65") = lFoV(.Offset(155, 4).Value, alwaysValues) 'MEA
                Sheets("Advanced Controls").Range("C66") = lFoV(.Offset(156, 4).Value, alwaysValues) 'LaTam
                Sheets("Advanced Controls").Range("C67") = lFoV(.Offset(157, 4).Value, alwaysValues) 'China
                Sheets("Advanced Controls").Range("C68") = lFoV(.Offset(158, 4).Value, alwaysValues) 'India
                Sheets("Advanced Controls").Range("C69") = lFoV(.Offset(159, 4).Value, alwaysValues) 'EU27
                Sheets("Advanced Controls").Range("C70") = lFoV(.Offset(160, 4).Value, alwaysValues) 'USA
                
                'PDS Adoption Scenario Inputs
                Sheets("Advanced Controls").Range("B228") = lFoV(.Offset(164, 4).Value, alwaysValues) 'Base custom scenario on
                Sheets("Advanced Controls").Range("B231") = lFoV(.Offset(165, 4).Value, alwaysValues) 'Regional Data Only?
                
                Select Case Sheets("Advanced Controls").Range("B228").Value
                Case "DEFAULT Linear", "DEFAULT S-Curve"
                    'Linear and S-Curve
                    Sheets("Advanced Controls").Range("B226").Value = "Default"
                    Sheets("Advanced Controls").Range("E238") = lFoV(.Offset(170, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E239") = lFoV(.Offset(171, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E240") = lFoV(.Offset(172, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E241") = lFoV(.Offset(173, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E242") = lFoV(.Offset(174, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E243") = lFoV(.Offset(175, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E244") = lFoV(.Offset(176, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E245") = lFoV(.Offset(177, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E246") = lFoV(.Offset(178, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E247") = lFoV(.Offset(179, 4).Value, alwaysValues)
                
                    If .Offset(181, 4).Value = "Default S-Curve (Logistic Model)" Then
                        Sheets("S-Curve Adoption").Range("J13").Value = "This Model"
                    ElseIf .Offset(181, 4).Value = "Alternate S-Curve (Bass Model)" Then
                        Sheets("S-Curve Adoption").Range("J13").Value = "Alternate"
                        
                        If .Offset(164, 4).Value = "DEFAULT S-Curve" Then
                            'Load Bass Model Parameters
                            'Bass Diffusion Model numbers - Innovation Parameter
                            Sheets("Advanced Controls").Range("J238") = lFoV(.Offset(170, 6).Value, alwaysValues)  'World
                            Sheets("Advanced Controls").Range("J239") = lFoV(.Offset(171, 6).Value, alwaysValues)  'OECD90
                            Sheets("Advanced Controls").Range("J240") = lFoV(.Offset(172, 6).Value, alwaysValues)  'Eastern Europe
                            Sheets("Advanced Controls").Range("J241") = lFoV(.Offset(173, 6).Value, alwaysValues)  'Asia SJapan
                            Sheets("Advanced Controls").Range("J242") = lFoV(.Offset(174, 6).Value, alwaysValues)  'Middle East + Africa
                            Sheets("Advanced Controls").Range("J243") = lFoV(.Offset(175, 6).Value, alwaysValues) 'Latam
                            Sheets("Advanced Controls").Range("J244") = lFoV(.Offset(176, 6).Value, alwaysValues)  'China
                            Sheets("Advanced Controls").Range("J245") = lFoV(.Offset(177, 6).Value, alwaysValues)  'India
                            Sheets("Advanced Controls").Range("J246") = lFoV(.Offset(178, 6).Value, alwaysValues)  'EU
                            Sheets("Advanced Controls").Range("J247") = lFoV(.Offset(179, 6).Value, alwaysValues)  'USA
                            
                            'Bass Diffusion Model numbers - Imitation Parameter
                            Sheets("Advanced Controls").Range("K238") = lFoV(.Offset(170, 7).Value, alwaysValues)  'World
                            Sheets("Advanced Controls").Range("K239") = lFoV(.Offset(171, 7).Value, alwaysValues)  'OECD90
                            Sheets("Advanced Controls").Range("K240") = lFoV(.Offset(172, 7).Value, alwaysValues)  'Eastern Europe
                            Sheets("Advanced Controls").Range("K241") = lFoV(.Offset(173, 7).Value, alwaysValues)  'Asia SJapan
                            Sheets("Advanced Controls").Range("K242") = lFoV(.Offset(174, 7).Value, alwaysValues)  'Middle East + Africa
                            Sheets("Advanced Controls").Range("K243") = lFoV(.Offset(175, 7).Value, alwaysValues)  'Latam
                            Sheets("Advanced Controls").Range("K244") = lFoV(.Offset(176, 7).Value, alwaysValues)  'China
                            Sheets("Advanced Controls").Range("K245") = lFoV(.Offset(177, 7).Value, alwaysValues)  'India
                            Sheets("Advanced Controls").Range("K246") = lFoV(.Offset(178, 7).Value, alwaysValues)  'EU
                            Sheets("Advanced Controls").Range("K247") = lFoV(.Offset(179, 7).Value, alwaysValues)  'USA
                
                        End If
                    End If
                        
                Case "Existing Adoption Prognostications"
                    'Existing Prognostications
                    Sheets("Advanced Controls").Range("B226").Value = "Custom"
                    Sheets("Advanced Controls").Range("B250") = lFoV(.Offset(184, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("B255") = lFoV(.Offset(185, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("C255") = lFoV(.Offset(186, 4).Value, alwaysValues)
                    
                Case "Customized S-Curve Adoption"
                    'Customized S-Curve
                    Sheets("Advanced Controls").Range("B226").Value = "Custom"
                    Sheets("Advanced Controls").Range("E251") = lFoV(.Offset(190, 4).Value, alwaysValues)
                    Sheets("Advanced Controls").Range("E254") = lFoV(.Offset(191, 4).Value, alwaysValues)
                
                Case Else '"Fully Customized PDS"
                    Sheets("Advanced Controls").Range("B226").Value = "Custom"
                    Sheets("Advanced Controls").Range("H250") = lFoV(.Offset(195, 4).Value, alwaysValues)
                End Select
                
                'REF ADOPTION SCENARIO INPUTS -------------------------------
                Sheets("Advanced Controls").Range("B264") = lFoV(.Offset(199, 4).Value, alwaysValues)  'REF Adoption Scenario Type
                If .Offset(199, 4).Value <> "Default" Then
                    Sheets("Advanced Controls").Range("B267") = lFoV(.Offset(200, 4).Value, alwaysValues)  'Custom REF Adoption Scenario
                End If
                Sheets("Advanced Controls").Range("B269") = lFoV(.Offset(201, 4).Value, alwaysValues)  'Use Regional Only?
                
                'ADDITIONAL VARIABLES -------------------------------
                Sheets("Advanced Controls").Range("B192") = lFoV(.Offset(207, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("C192") = lFoV(.Offset(208, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("D192") = lFoV(.Offset(209, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("E192") = lFoV(.Offset(210, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("F192") = lFoV(.Offset(211, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("G192") = lFoV(.Offset(212, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("H192") = lFoV(.Offset(213, 4).Value, alwaysValues)
                Sheets("Advanced Controls").Range("B207") = lFoV(.Offset(207, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("C207") = lFoV(.Offset(208, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("D207") = lFoV(.Offset(209, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("E207") = lFoV(.Offset(210, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("F207") = lFoV(.Offset(211, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("G207") = lFoV(.Offset(212, 8).Value, alwaysValues)
                Sheets("Advanced Controls").Range("H207") = lFoV(.Offset(213, 8).Value, alwaysValues)
                
                'OTHER INPUTS -------------------------------
                'Adoption Adjustment
                Y_PDS = Split(.Offset(218, 4).Value, ",")
                Y_REF = Split(.Offset(219, 4).Value, ",")
                'Reset all cells
                For yr = 2014 To 2060
                    Sheets("Advanced Controls").Cells(yr - 1737, 6).Value = "N"
                Next
                'Then set required cells
                For yr = 0 To UBound(Y_PDS) - 1
                    Sheets("Advanced Controls").Cells(CInt(Y_PDS(yr)) - 1737, 6).Value = "Y-PDS"
                Next
                
                For yr = 0 To UBound(Y_REF) - 1
                    Sheets("Advanced Controls").Cells(CInt(Y_REF(yr)) - 1737, 6).Value = "Y-REF"
                Next
                                
                If calledDirectly Then
                    If Sheets("Advanced Controls").Visible = True Then
                        Sheets("Advanced Controls").Activate
                        Range("A3:F6").Select
                        ActiveWindow.ScrollColumn = 1
                    End If
                End If
            End With
        Else 'For cases where the Sub call was from Basic Controls, indicate that user cancelled
            If Not calledDirectly Then
                Sheets("Basic Controls").Range("I12").Value = "Not Loaded"
            End If
        End If
    Else
        MsgBox ("Scenario Not Found!")
        Range("B9").Value = ""
    End If
        
    If calledDirectly Then
        Application.ScreenUpdating = True
        Application.Calculation = xlAutomatic
    End If
Else
    MsgBox ("Please Select a Scenario in Green Cell B9 of ScenarioRecord")
End If

End Sub

Sub CopyCurrentAsCustom()
'
'   CopyCurrentAsCustom Macro
'   Allows you to create a custom adoption scenario by copying the currently loaded adoption scenario

'   Perform required checks first:

continue = False
overWrite = 0
If IsError(Application.Sum(Sheets("Helper Tables").Range("C91:C137").Value)) Or Application.Sum(Sheets("Helper Tables").Range("C91:C137").Value) = 0 Then
    MsgBox ("There Seems to be No Adoption Scenario Loaded or Some other Error, Please Verify an Adoption Scenario is Producing Results.")
Else
    currBlock = 1
    startRow = 23
    blockSize = 54
    Do While (Left(Cells(startRow + currBlock * blockSize, 2).Value, 14) <> "[Type Scenario") And currBlock < 11
        currBlock = currBlock + 1
    Loop
    If currBlock >= 11 Then
        respo = MsgBox("All 10 Custom PDS Adoption Scenario Slots are Filled. Do you Want to OverWrite an Existing Scenario?", vbYesNo)
        If respo = vbYes Then
            overWrite = Application.InputBox("Please Enter the Number of the PDS Scenario That You Want to Overwrite.", , , , , , , 1)
            If overWrite > 0 And overWrite < 11 Then
                respo = MsgBox("Are You Sure You Want to Replace Custom PDS Scenario:#" + CStr(overWrite) + " " + Cells(startRow + overWrite * blockSize, 2).Value, vbYesNo + vbExclamation, "Replace Custom PDS Scenario.")
                If respo = vbYes Then
                    continue = True
                Else
                    MsgBox ("Nothing Replaced, No New Custom PDS Scenario Saved")
                End If
            Else
                MsgBox ("No Custom PDS Scenario Found with that Number. Only Scenarios 1 through 10 are Available. Nothing Replaced, No New Custom PDS Scenario Saved.")
            End If
        Else
            MsgBox ("No New Custom PDS Scenario Saved.")
        End If
    Else 'Empty Custom Scenario Block Found
        continue = True
    End If
End If

If continue Then 'Save New Custom Scenario
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("Helper Tables").Activate
    
    If overWrite = 0 Then
        newScenarioID = currBlock
    Else
        newScenarioID = overWrite
    End If
    Name = ""
    Name = Application.InputBox("Please Enter the Name for this Custom PDS Scenario. This Will be Used on Advanced Controls.", "Save New Custom PDS Scenario", "Custom PDS Scenario " + CStr(newScenarioID) + ": ", , , , , 2)
    If Name <> "" And Name <> False Then
        Sheets("Custom PDS Adoption").Activate
        Cells(startRow + newScenarioID * blockSize, 2).Value = Name
        
        'Copy World Values
        Sheets("Helper Tables").Activate
        Range("C91").Select
        Range(Selection, Selection.End(xlDown)).Select
        Selection.Copy
        Sheets("Custom PDS Adoption").Select
        Range(Cells(startRow + newScenarioID * blockSize + 4, 2), Cells(startRow + newScenarioID * blockSize + 50, 2)).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
            :=False, Transpose:=False
        
        'Now Copy Regions and Countries
        For region = 1 To 9
            Sheets("Helper Tables").Activate
            If Application.Sum(Range(Cells(91, 3 + region), Cells(137, 3 + region)).Value) > 0 Then
                Range(Cells(91, 3 + region), Cells(137, 3 + region)).Select
                Selection.Copy
                Sheets("Custom PDS Adoption").Select
                Range(Cells(startRow + newScenarioID * blockSize + 4, 2 + region), Cells(startRow + newScenarioID * blockSize + 50, 2 + region)).Select
                Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
                    :=False, Transpose:=False
            End If
        Next
    
        MsgBox ("The Data Have Been Copied, but the Description, Sources, Assumptions, Units and Equations Must Be Filled Out Directly on the Sheet. Note that This Scenario Has Not Been Yet Loaded Into the Model (Select on Advanced Controls). Click 'OK' and Complete the Fields Fully.")
        Sheets("Custom PDS Adoption").Activate
        Range(Cells(startRow + newScenarioID * blockSize + 2, 14), Cells(startRow + newScenarioID * blockSize + 27, 27)).Select
        ActiveWindow.ScrollRow = startRow + newScenarioID * blockSize
        ActiveWindow.ScrollColumn = 12
    Else
        MsgBox ("No New Custom PDS Scenario Saved.")
    End If
    
    Application.Calculation = xlAutomatic
    Application.ScreenUpdating = True
    'Sheets("Helper Tables").Visible = xlSheetHidden
    Sheets("Custom PDS Adoption").Activate
End If
End Sub

Sub CopyCurrentAsCustomREF()
'
'   CopyCurrentAsCustom Macro
'   Allows you to create a custom REF adoption scenario by copying the currently loaded adoption scenario

'   Perform required checks first:

continue = False
overWrite = 0
If IsError(Application.Sum(Sheets("Helper Tables").Range("C91:C137").Value)) Or Application.Sum(Sheets("Helper Tables").Range("C91:C137").Value) = 0 Then
    MsgBox ("There Seems to be No Adoption Scenario Loaded or Some other Error, Please Verify an Adoption Scenario is Producing Results.")
Else
    currBlock = 1
    startRow = 23
    blockSize = 54
    Do While (Left(Cells(startRow + currBlock * blockSize, 2).Value, 14) <> "[Type Scenario") And currBlock < 11
        currBlock = currBlock + 1
    Loop
    If currBlock >= 11 Then
        respo = MsgBox("All 10 Custom REF Adoption Scenario Slots are Filled. Do you Want to OverWrite an Existing Scenario?", vbYesNo)
        If respo = vbYes Then
            overWrite = Application.InputBox("Please Enter the Number of the REF Scenario That You Want to Overwrite.", , , , , , , 1)
            If overWrite > 0 And overWrite < 11 Then
                respo = MsgBox("Are You Sure You Want to Replace Custom REF Scenario:#" + CStr(overWrite) + " " + Cells(startRow + overWrite * blockSize, 2).Value, vbYesNo + vbExclamation, "Replace Custom REF Scenario.")
                If respo = vbYes Then
                    continue = True
                Else
                    MsgBox ("Nothing Replaced, No New Custom REF Scenario Saved")
                End If
            Else
                MsgBox ("No Custom REF Scenario Found with that Number. Only Scenarios 1 through 10 are Available. Nothing Replaced, No New Custom REF Scenario Saved.")
            End If
        Else
            MsgBox ("No New Custom REF Scenario Saved.")
        End If
    Else 'Empty Custom Scenario Block Found
        continue = True
    End If
End If

If continue Then 'Save New Custom Scenario
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("Helper Tables").Activate
    
    If overWrite = 0 Then
        newScenarioID = currBlock
    Else
        newScenarioID = overWrite
    End If
    Name = ""
    Name = Application.InputBox("Please Enter the Name for this Custom REF Scenario. This Will be Used on Advanced Controls.", "Save New Custom REF Scenario", "Custom REF Scenario " + CStr(newScenarioID) + ": ", , , , , 2)
    If Name <> "" And Name <> False Then
        Sheets("Custom REF Adoption").Activate
        Cells(startRow + newScenarioID * blockSize, 2).Value = Name
        
        'Copy World Values
        Sheets("Helper Tables").Activate
        Range("C91").Select
        Range(Selection, Selection.End(xlDown)).Select
        Selection.Copy
        Sheets("Custom REF Adoption").Select
        Range(Cells(startRow + newScenarioID * blockSize + 4, 2), Cells(startRow + newScenarioID * blockSize + 50, 2)).Select
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
            :=False, Transpose:=False
        
        'Now Copy Regions and Countries
        For region = 1 To 9
            Sheets("Helper Tables").Activate
            If Application.Sum(Range(Cells(91, 3 + region), Cells(137, 3 + region)).Value) > 0 Then
                Range(Cells(91, 3 + region), Cells(137, 3 + region)).Select
                Selection.Copy
                Sheets("Custom REF Adoption").Select
                Range(Cells(startRow + newScenarioID * blockSize + 4, 2 + region), Cells(startRow + newScenarioID * blockSize + 50, 2 + region)).Select
                Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
                    :=False, Transpose:=False
            End If
        Next
    
        MsgBox ("The Data Have Been Copied, but the Description, Sources, Assumptions, Units and Equations Must Be Filled Out Directly on the Sheet. Note that This Scenario Has Not Been Yet Loaded Into the Model (Select on Advanced Controls). Click 'OK' and Complete the Fields Fully.")
        Sheets("Custom REF Adoption").Activate
        Range(Cells(startRow + newScenarioID * blockSize + 2, 14), Cells(startRow + newScenarioID * blockSize + 27, 27)).Select
        ActiveWindow.ScrollRow = startRow + newScenarioID * blockSize
        ActiveWindow.ScrollColumn = 12
    Else
        MsgBox ("No New Custom REF Scenario Saved.")
    End If
    
    Application.Calculation = xlAutomatic
    Application.ScreenUpdating = True
    'Sheets("Helper Tables").Visible = xlSheetHidden
    Sheets("Custom REF Adoption").Activate
End If
End Sub

Sub DeleteCustomPDS_Click()
'
' Identifies and Deletes the record from this sheet

If Sheets("Custom PDS Adoption").Range("G12").Value <> "" Then
    If Left(Sheets("Custom PDS Adoption").Range("G12").Value, 15) <> "[Type Scenario " Then
        Application.ScreenUpdating = False
        Application.Calculation = xlManual
        Sheets("Custom PDS Adoption").Activate
        
        'Set key input variables
        Dim stepSize As Integer: stepSize = 54 'rows
        Dim firstRow As Integer: firstRow = 77
        Dim currRow As Integer: currRow = firstRow
        Dim block As Integer: block = 1
        Dim Name As String: Name = Range("G12").Value
        Dim respo As Integer
        Dim stamp As Long
        Dim num As Integer
        
        'Find block of selected scenario
        Do While Not Name = Cells(currRow, 2).Value And currRow < 620 'Prevent searching for nonexistent scenarios
            currRow = currRow + stepSize
            block = block + 1
        Loop
        
        If currRow < 620 Then 'match found
            respo = MsgBox("Are you sure you want to delete """ & Name & """?", vbYesNo, "Delete Scenario")
            If respo = vbYes Then 'Delete
                With Cells(currRow, 1)
                    'Rename Record
                    .Offset(0, 1).Value = "[Type Scenario " & block & " Name Here...]"
                
                    'Delete Data
                    Range(.Offset(2, 1), .Offset(50, 10)).Select
                    Selection.ClearContents
                    'Delete Description and Supporting Data
                    Range(.Offset(2, 13), .Offset(50, 48)).Select
                    Selection.ClearContents
                    Range("BJ21:CR68").Copy
                    Application.DisplayAlerts = False
                    .Offset(2, 13).Select
                    ActiveSheet.Paste
                    Application.DisplayAlerts = True
                End With
            End If
        Else
            MsgBox ("Scenario Not Found!, Nothing Deleted.")
            Range("G12").Value = ""
        End If
            
        Application.ScreenUpdating = True
        Application.Calculation = xlAutomatic
    Else
        MsgBox ("That is either a blank record or the name was not properly set for that scenario. If the scenario exists, please rename to a descriptive name")
    End If
Else
    MsgBox ("Please Select a Custom Scenario in Green Cell G12 of Custom PDS Adoption")
End If
End Sub

Sub DeleteCustomREF_Click()
'
' Identifies and Deletes the record from this sheet

If Sheets("Custom REF Adoption").Range("G12").Value <> "" Then
    If Left(Sheets("Custom REF Adoption").Range("G12").Value, 15) <> "[Type Scenario " Then
        Application.ScreenUpdating = False
        Application.Calculation = xlManual
        Sheets("Custom REF Adoption").Activate
        
        'Set key input variables
        Dim stepSize As Integer: stepSize = 54 'rows
        Dim firstRow As Integer: firstRow = 77
        Dim currRow As Integer: currRow = firstRow
        Dim block As Integer: block = 1
        Dim Name As String: Name = Range("G12").Value
        Dim respo As Integer
        Dim stamp As Long
        Dim num As Integer
        
        'Find block of selected scenario
        Do While Not Name = Cells(currRow, 2).Value And currRow < 620 'Prevent searching for nonexistent scenarios
            currRow = currRow + stepSize
            block = block + 1
        Loop
        
        If currRow < 620 Then 'match found
            respo = MsgBox("Are you sure you want to delete """ & Name & """?", vbYesNo, "Delete Scenario")
            If respo = vbYes Then 'Delete
                With Cells(currRow, 1)
                    'Rename Record
                    .Offset(0, 1).Value = "[Type Scenario " & block & " Name Here (REF CASE)...]"
                
                    'Delete Data
                    Range(.Offset(2, 1), .Offset(50, 10)).Select
                    Selection.ClearContents
                    'Delete Description and Supporting Data
                    Range(.Offset(2, 13), .Offset(50, 48)).Select
                    Selection.ClearContents
                    Range("BJ21:CR68").Copy
                    Application.DisplayAlerts = False
                    .Offset(2, 13).Select
                    ActiveSheet.Paste
                    Application.DisplayAlerts = True
                End With
            End If
        Else
            MsgBox ("Scenario Not Found!, Nothing Deleted.")
            Range("G12").Value = ""
        End If
            
        Application.ScreenUpdating = True
        Application.Calculation = xlAutomatic
    Else
        MsgBox ("That is either a blank record or the name was not properly set for that scenario. If the scenario exists, please rename to a descriptive name")
    End If
Else
    MsgBox ("Please Select a Custom Scenario in Green Cell G12 of Custom REF Adoption")
End If
End Sub

Function sFoV(sourceRange As Range, rowNum As Variant)
    'This Function determines if a Range in the model has a Function or Value
    ' and formats the result of a Formula for storage on the ScenarioRecord
    ' Note: to prevent decimal separator issues, the formula is always stored with "." as the decimal separator
    ' and "," as the thousands separator, and converts according to local machine settings.
    Dim funcString As String
    Dim listSep As String
    Dim decSep As String

    If sourceRange.HasFormula Then
        funcString = CStr(sourceRange.Formula)
        'Ensure that the Decimal Separator is "." and the List Separator is ","
        listSep = Application.International(xlListSeparator)
        decSep = Application.International(xlDecimalSeparator)
        If listSep <> "," Or decSep <> "." Then
            funcString = Replace(funcString, listSep, "#$%")
            funcString = Replace(funcString, decSep, ".")
            funcString = Replace(funcString, "#$%", ",")
        End If
        sFoV = "Val:(" + CStr(sourceRange.Value) + ") Formula:" + funcString
        'Record the language that the formulae have been recorded in
        'Test the conditional compiler constant #Mac
        #If Mac Then ' Mac
            Sheets("ScenarioRecord").Cells(rowNum + 4, 14).Value = Application.LocalizedLanguage
        #Else ' Windows
            Sheets("ScenarioRecord").Cells(rowNum + 4, 14).Value = Application.LanguageSettings.LanguageID(msoLanguageIDUI)
        #End If
    Else
        If (IsNumeric(sourceRange.Value)) And (sourceRange.Value <> "") Then
            sFoV = CDbl(sourceRange.Value)
        Else
            sFoV = sourceRange.Value
        End If
    End If
    
End Function

Function lFoV(sourceValue As Variant, alwaysVal As Boolean)
    'This Function determines if a record on the ScenarioRecord has a Function or Value
    ' and passes the formula or value to the input ranges in the model
    ' Note: to prevent decimal separator issues, the formula is always stored with "." as the decimal separator
    ' and "," as the thousands separator, and converts according to local machine settings.
    Dim funcString As String
    Dim listSep As String
    Dim decSep As String
    If Left(CStr(sourceValue), 4) = "Val:" Then
        If Not alwaysVal Then
            lFoV = Right(sourceValue, Len(sourceValue) - (7 + InStr(1, sourceValue, "Formula:")))
        Else
            endofNum = InStr(1, sourceValue, ")")
            result = Mid(sourceValue, 6, endofNum - 6)
            lFoV = CDbl(result)
        End If
    Else
        lFoV = sourceValue
    End If
    
End Function



Sub clear_C_prices()
    Dim respo As Long
    Dim Scenario As String
    Scenario = Worksheets("Carbon Price Analysis").Range("H15").Value
    respo = MsgBox("Are you sure you want to clear out all existing Carbon Prices from " & Scenario & "?", vbYesNo, "Clear Carbon Prices")
    If respo = vbYes Then
        With Worksheets("Carbon Price Analysis")
            Select Case Scenario
            Case "Scenario 1"
                .Range("C29:C74").ClearContents
            Case "Scenario 2"
                .Range("J29:J74").ClearContents
            Case "Scenario 3"
                .Range("Q29:Q74").ClearContents
            End Select
        End With
    End If
End Sub

Sub add_C_prices()
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Dim startYear As Long
    Dim endYear As Long
    Dim startPrice As Double
    Dim endPrice As Double
    Dim growthType As String
    Dim increment As Double
    Dim currYear As Long
    Dim Scenario As Long
    
    With Worksheets("Carbon Price Analysis")
        startYear = .Range("G17"): currYear = startYear
        endYear = .Range("G19")
        startPrice = .Range("H17")
        Scenario = CInt(Right(.Range("H15"), 1))
        If .Range("G15").Value = "Linear Growth" Then
            endPrice = .Range("H19")
            growthType = "linear"
            increment = (endPrice - startPrice) / (endYear - startYear)
            
            Do While currYear <= endYear
                Cells(currYear - 1986, 3 + (Scenario - 1) * 7).Value = startPrice + (currYear - startYear) * increment
                currYear = currYear + 1
            Loop
        Else
            growthType = "fixed"
            
            Do While currYear <= endYear
                Cells(currYear - 1986, 3 + (Scenario - 1) * 7).Value = startPrice
                currYear = currYear + 1
            Loop
        End If
        
    End With

    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
End Sub


Sub updateBasicControls()
    'Copies Key Variables inputs from Basic Controls to Advanced Controls and recalculates model results
    
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Sheets("Basic Controls").Activate
    
    Dim Source() As String 'Cell addresses on 'Basic Controls'!
    Dim Destin() As String 'Cell addresses on 'Advanced Controls'!
    Const fuelTypeCONV = "H144" 'The input cell for Conventional Fuel Type
    Const fueltypeSOL = "H148"  ' The input cell for Solution Fuel Type
    Const fuelInputConventional = "F144"  ' The Input cell for Fuel Emissions - Conventional
    Const fuelInputSolution = "G144"  ' The Input cell for Fuel Emissions - Solution
    Const alt_GridInputSolution = "C144"  ' The alternative Grid Input - Solution
    Dim ElectricityUsedConventional As Boolean
    Dim ElectricityUsedSolution As Boolean
    Dim i As Long
    Dim j As Long
    Dim useCustomAdoption As Boolean: useCustomAdoption = False
    Dim useExistingAdoption As Boolean: useExistingAdoption = False
    Const CustomSelector = "G30" 'On Basic Controls
    Const AdoptionSelector = "C30" 'On Basic Controls
    Const AdoptionScenarioInput = "B228" 'On Advanced Controls
        
    Source = Split("C6," & "C11," & "C12," & "C14," & "C15," & "G14," & "G15," & "C17," & "C18," & "G17," & "G18," & "C22," & "C23," & "G22," & "G23," & "C25," & "C26," & "G25," & "G26," & "C30," & "G30", ",")
    Destin = Split("B55," & "B98," & "B113," & "K98," & "K113," & "C98," & "C113," & "I98," & "I113," & "H98," & "H113," & "B144," & "D144," & "F144," & "G144," & "C159," & "D159," & "F159," & "G159," & "B250," & "H250", ",")

    '    ___________________________________________________________________________________
    
    'Test for whether each adoption case selector is enabled and a case selected
    If Sheets("Basic Controls").Range(CustomSelector).Value <> "" Then useCustomAdoption = True
    If Sheets("Basic Controls").Range(AdoptionSelector).Value <> "" Then useExistingAdoption = True
    
    If useExistingAdoption And useCustomAdoption Then
        MsgBox ("You have entered two adoption cases, please delete either the Existing Projection Selection or the Customized Drawdown Selection. Nothing Loaded.")
    Else
        ElectricityUsedConventional = (StrComp(Sheets("Advanced Controls").Range(fuelTypeCONV).Value, "Commercial Electricity", 1) = 0 Or _
            StrComp(Sheets("Advanced Controls").Range(fuelTypeCONV).Value, "Electricity to Consumer", 1) = 0)
        ElectricityUsedSolution = (StrComp(Sheets("Advanced Controls").Range(fueltypeSOL).Value, "Commercial Electricity", 1) = 0 Or _
            StrComp(Sheets("Advanced Controls").Range(fueltypeSOL).Value, "Electricity to Consumer", 1) = 0)
        
        For i = LBound(Destin) To UBound(Destin)
            If Not (ElectricityUsedConventional And StrComp(Destin(i), fuelInputConventional, 1) = 0) Then
                'No fuel emissions entered when only Electricity Used
                If Not (ElectricityUsedSolution And StrComp(Destin(i), fuelInputSolution, 1) = 0) Then
                    Sheets("Advanced Controls").Range(Destin(i)).Value = Range(Source(i)).Value
                End If
            End If
        Next
    End If
    
    'Set Adoption Scenario Controls on Advanced Controls
    If useCustomAdoption Then
        Sheets("Advanced Controls").Range(AdoptionScenarioInput).Value = "Fully Customized PDS"
        Sheets("Advanced Controls").Range(AdoptionScenarioInput).Offset(-2, 0).Value = "Custom"
    ElseIf useExistingAdoption Then
        Sheets("Advanced Controls").Range(AdoptionScenarioInput).Value = "Existing Adoption Prognostications"
        Sheets("Advanced Controls").Range(AdoptionScenarioInput).Offset(-2, 0).Value = "Custom"
    End If
    
    Sheets("Advanced Controls").Range(alt_GridInputSolution).Value = ""
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
End Sub

Sub loadBasicControls()
'Loads the Scenario Selected on Basic Controls into Model, updates results, and shows key inputs used on Basic Controls

If Sheets("Basic Controls").Range("C5").Value <> "" Then
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Dim Source() As String 'Cell addresses on 'Advanced Controls'!
    Dim Destin() As String 'Cell addresses on 'Basic Controls'!
    Const gridInputConventional = "B144"  ' The Input cell for Grid Emissions - Conventional
    Const gridInputSolution = "D144"  ' The Input cell for Grid Emissions - Solution
    Const basicGridInputSolution = "C23"  ' The Grid Emissions Input on Basic Controls - Solution
    Const alt_GridInputSolution = "C144"  ' The alternative Input cell for Grid Emissions - Solution
    Const basicScenarioIndicator = "I12"  'Used to Indicate whether a scenario was loaded by ScenarioRecorder
    Dim i As Long
    Dim alwaysBlue() As String
    Dim adoptionScenarios() As String
    Dim adoptionRecordStart() As Variant
    Dim hideAdoption As Boolean: hideAdoption = True
    Dim hideCustom As Boolean: hideCustom = True
    Const CustomSelector = "G30" 'On Basic Controls
    Const AdoptionSelector = "C30" 'On Basic Controls
    Const AdoptionMessage = "D28" 'On Basic Controls
    Dim currRow As Integer: currRow = gFirstRow
    Destin = Split("C6," & "C11," & "C12," & "C14," & "C15," & "G14," & "G15," & "C17," & "C18," & "G17," & "G18," & "C22," & "C23," & "G22," & "G23," & "C25," & "C26," & "G25," & "G26," & "C30," & "G30", ",")
    Source = Split("B55," & "B98," & "B113," & "K98," & "K113," & "C98," & "C113," & "I98," & "I113," & "H98," & "H113," & "B144," & "D144," & "F144," & "G144," & "C159," & "D159," & "F159," & "G159," & "B250," & "H250", ",")
    alwaysBlue = Split("C6", ",")
    'Find correct Adoption Choice cell on Advanced Controls
    adoptionScenarios = Split("A255,A228,A243,A241", ",")
    adoptionRecordStart = Array(231, 164, 164, 231) 'Row in each ScenarioRecord where the Adoption Scenario is stored, matched to adoptionScenarios
   
    
    Sheets("ScenarioRecord").Range("B9").Value = Range("C5").Value
    
    '    ___________________________________________________________________________________
        
    Call LoadScenario_Click(False)
    Application.Calculate
    Sheets("Basic Controls").Activate
    Sheets("Basic Controls").Unprotect
    
    If StrComp(Range(basicScenarioIndicator).Value, "Not Loaded", 1) <> 0 Then
        For i = LBound(Destin) To UBound(Destin)
            With Sheets("Basic Controls").Range(Destin(i))
                .Value = Sheets("Advanced Controls").Range(Source(i)).Value
                If (.Value = 0 Or .Value = "") Or (UBound(Filter(alwaysBlue, Destin(i))) > -1) Then   'Make Cell Blue
                    .Interior.Pattern = xlSolid
                    .Interior.PatternColorIndex = xlAutomatic
                    .Interior.ThemeColor = xlThemeColorAccent1
                    .Interior.TintAndShade = 0.399975585192419
                    .Interior.PatternTintAndShade = 0
                Else ' Make cell Green
                    .Interior.Pattern = xlSolid
                    .Interior.PatternColorIndex = xlAutomatic
                    .Interior.ThemeColor = xlThemeColorAccent6
                    .Interior.TintAndShade = 0.599993896298105
                    .Interior.PatternTintAndShade = 0
                End If
                .Validation.InputTitle = "Default Value:"
                If Sheets("Advanced Controls").Range(Source(i)).Value > 1000 Then 'format with thousands
                    .Validation.InputMessage = Format(Sheets("Advanced Controls").Range(Source(i)).Value, "#,##0.00")
                Else
                    If Sheets("Advanced Controls").Range(Source(i)).Value < 0.01 Then 'format with decimals
                        .Validation.InputMessage = Format(Sheets("Advanced Controls").Range(Source(i)).Value, "0.00000")
                    Else
                        .Validation.InputMessage = Format(Sheets("Advanced Controls").Range(Source(i)).Value, "0.0000")
                    End If
                End If
            End With
        Next
        If StrComp(Sheets("Advanced Controls").Range(gridInputSolution).Value, "", 1) = 0 And StrComp(Sheets("Advanced Controls").Range(alt_GridInputSolution).Value, "", 1) <> 0 Then
            'Convert the Grid Emissions Units for Basic Controls, and Update the Validation Message
            Sheets("Basic Controls").Range(basicGridInputSolution).Value = (1 - Sheets("Advanced Controls").Range(alt_GridInputSolution).Value) * Sheets("Advanced Controls").Range(gridInputConventional).Value
            Sheets("Basic Controls").Range(basicGridInputSolution).Validation.InputMessage = Format(Sheets("Basic Controls").Range(basicGridInputSolution).Value, "0.000")
        End If
        
        'Set the Description of the Scenario

        With Sheets("Basic Controls").Range("C5")
            'Find block of selected scenario on ScenarioRecord
            Do While Not .Value = Sheets("ScenarioRecord").Cells(currRow, 5).Value And currRow < 10 + gStepSize * (1 + Sheets("ScenarioRecord").Range("D1").Value) 'Prevent searching for nonexistent scenarios
                currRow = currRow + gStepSize
            Loop
            .Validation.InputTitle = Left(.Value, 32)
            .Validation.InputMessage = Left(Sheets("ScenarioRecord").Cells(currRow + 1, 5), 254)
        End With
        'Load the Adoption Scenarios
        i = 0
        Do While Sheets("Advanced Controls").Range(adoptionScenarios(i)).Value <> "Base Adoption on:"
            i = i + 1
        Loop
        With Sheets("Advanced Controls").Range(adoptionScenarios(i)).Offset(0, 1)
            'Check the Selected Adoption on Advanced Controls
            If .Value = "Fully Customized PDS" Then 'Place message to indicate Custom adoption curves used
                Sheets("Basic Controls").Range(AdoptionMessage).Value = "Loaded Scenario Uses a Customized Drawdown Adoption Curve"
                Sheets("Basic Controls").Range(AdoptionSelector).Value = ""
                Sheets("Basic Controls").Range(AdoptionSelector).Validation.InputMessage = ""
            ElseIf .Value = "Existing Adoption Prognostications" Then 'Place message to indicate Existing Prognostications used
                Sheets("Basic Controls").Range(AdoptionMessage).Value = "Loaded Scenario Uses an Existing Projection"
                Sheets("Basic Controls").Range(CustomSelector).Value = ""
                Sheets("Basic Controls").Range(CustomSelector).Validation.InputMessage = ""
            Else
                Sheets("Basic Controls").Range(AdoptionMessage).Value = "Loaded Scenario Uses Neither an Existing Projection Nor a Custom Adoption"
                Sheets("Basic Controls").Range(AdoptionSelector).Value = ""
                Sheets("Basic Controls").Range(CustomSelector).Value = ""
                Sheets("Basic Controls").Range(AdoptionSelector).Validation.InputMessage = ""
                Sheets("Basic Controls").Range(CustomSelector).Validation.InputMessage = ""
            End If
        End With
            
        'Check the Selected Adoption for Each Stored Scenario. If no scenario uses a particular adoption type, then disable it
        For j = 1 To Sheets("ScenarioRecord").Range("D1").Value
            With Sheets("ScenarioRecord").Range("E" + CStr(gFirstRow + adoptionRecordStart(i) + j * gStepSize))
                If .Value = "Fully Customized PDS" Then
                    hideCustom = False
                ElseIf .Value = "Existing Adoption Prognostications" Then
                    hideAdoption = False
                End If
            End With
        Next
        
        If hideCustom Then '"disable" Custom Selector
            Sheets("Basic Controls").Range(CustomSelector).Value = ""
            With Sheets("Basic Controls").Range(CustomSelector)
                .Interior.Pattern = xlSolid
                .Interior.PatternColorIndex = xlAutomatic
                .Interior.ThemeColor = xlThemeColorDark1
                .Interior.TintAndShade = -4.99893185216834E-02
                .Interior.PatternTintAndShade = 0
            End With
            With Sheets("Basic Controls").Range(CustomSelector).Offset(0, -1)
                .Font.Color = RGB(191, 191, 191)
            End With
        Else ' Ensure the Selector has proper formatting for input/Enable it
            With Sheets("Basic Controls").Range(CustomSelector)
                .Interior.Pattern = xlSolid
                .Interior.PatternColorIndex = xlAutomatic
                .Interior.ThemeColor = xlThemeColorAccent6
                .Interior.TintAndShade = 0.599993896298105
                .Interior.PatternTintAndShade = 0
            End With
            With Sheets("Basic Controls").Range(CustomSelector).Offset(0, -1)
                .Font.ColorIndex = xlAutomatic
                .Font.TintAndShade = 0
            End With
        End If
        If hideAdoption Then ' "disable" Existing Projection Selector
            Sheets("Basic Controls").Range(AdoptionSelector).Value = ""
            With Sheets("Basic Controls").Range(AdoptionSelector)
                .Interior.Pattern = xlSolid
                .Interior.PatternColorIndex = xlAutomatic
                .Interior.ThemeColor = xlThemeColorDark1
                .Interior.TintAndShade = -4.99893185216834E-02
                .Interior.PatternTintAndShade = 0
            End With
            With Sheets("Basic Controls").Range(AdoptionSelector).Offset(0, -1)
                .Font.Color = RGB(191, 191, 191)
            End With
        Else ' Ensure the Selector has proper formatting for input/Enable it
            With Sheets("Basic Controls").Range(AdoptionSelector)
                .Interior.Pattern = xlSolid
                .Interior.PatternColorIndex = xlAutomatic
                .Interior.ThemeColor = xlThemeColorAccent6
                .Interior.TintAndShade = 0.599993896298105
                .Interior.PatternTintAndShade = 0
            End With
            With Sheets("Basic Controls").Range(AdoptionSelector).Offset(0, -1)
                .Font.ColorIndex = xlAutomatic
                .Font.TintAndShade = 0
            End With
        End If
    Else
        'The User Cancelled the Scenario Load, reset indicator cell
        Range(basicScenarioIndicator).Value = ""
    End If
    Sheets("Basic Controls").Protect
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
Else
    MsgBox ("No Scenario Selected on Basic Controls. Nothing to Load.")
End If
End Sub

Sub savePublic(stamp As String)
    'Mainly used in the code that prepares the model for public use which is deleted, this is the remaining portion.
    ' Delete the current sheet with this current code
    Application.DisplayAlerts = False
    Sheets("Instructions").Delete
    Application.DisplayAlerts = True
    'Save a separate copy of Public Model and Internal Model
    respo = MsgBox("SaveAs Public Version of Model? (Name: " & "'Drawdown-" & Sheets("Advanced Controls").Range("EnterSolutionName").Value & "_" & Sheets("Welcome").Range("I1").Value & "v1.1_" & stamp & "_PUBLIC.xlsm')", vbYesNo, "Prepare for Public")
    If respo = vbYes Then
        ActiveWorkbook.SaveAs Filename:= _
            Application.ActiveWorkbook.Path & "\Drawdown-" & Sheets("Advanced Controls").Range("EnterSolutionName").Value & "_" & _
                Sheets("Welcome").Range("I1").Value & "_v" & Sheets("Welcome").Range("K1").Value & "_" & stamp & "_PUBLIC.xlsm", _
                FileFormat:=xlOpenXMLWorkbookMacroEnabled, CreateBackup:=False
    End If
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
End Sub

Sub savePDF()
    Dim currScr As Long
    Dim currCalc As Long
    Dim stamp As String
    Dim fname As String
    Dim fileAddress As Variant
    Dim i As Integer
    
    'Calculates the Payback for every year of analysis
    'Saves a PDF of the VarableSummary or DetailedResults sheets
    If ActiveSheet.Name = "Variable Summary" Or ActiveSheet.Name = "Detailed Results" Then
        'Save Status
        currScr = Application.ScreenUpdating
        currCalc = Application.Calculation
        Application.ScreenUpdating = False
        Application.Calculation = xlManual
        Application.DisplayAlerts = True
        stamp = DatePart("d", DateTime.Now()) & WorksheetFunction.Text(Date, "[$-409]mmm") & DatePart("yyyy", DateTime.Now())
        If ActiveSheet.Name = "Variable Summary" Then
            fname = Application.ActiveWorkbook.Path & "\Drawdown-" & Sheets("Advanced Controls").Range("EnterSolutionName").Value & _
                "_" & stamp & "_" & "Variables" & ".pdf"
                        
            With Excel.Application.FileDialog(msoFileDialogSaveAs)
                For i = 1 To .Filters.Count
                    If InStr(.Filters(i).Extensions, "pdf") <> 0 Then Exit For
                Next i
            
                .FilterIndex = i
                .InitialFileName = fname
                .Title = "Select Folder and FileName to save"
            
                If CBool(.Show) Then
                    fileAddress = .SelectedItems.Item(.SelectedItems.Count)
                End If
            
                If fileAddress <> "" Then
                    ActiveSheet.ExportAsFixedFormat _
                    Filename:=fileAddress, _
                    Type:=xlTypePDF, _
                    Quality:=xlQualityStandard, _
                    IncludeDocProperties:=True, _
                    IgnorePrintAreas:=False, _
                    OpenAfterPublish:=True
                End If
                    
            End With

        Else ''Detailed Results'
            fname = Application.ActiveWorkbook.Path & "\Drawdown-" & Sheets("Advanced Controls").Range("EnterSolutionName").Value & _
                "_" & stamp & "_" & "Results" & ".pdf"
                        
            With Excel.Application.FileDialog(msoFileDialogSaveAs)
                For i = 1 To .Filters.Count
                    If InStr(.Filters(i).Extensions, "pdf") <> 0 Then Exit For
                Next i
            
                .FilterIndex = i
                .InitialFileName = fname
                .Title = "Select Folder and FileName to save"
            
                If CBool(.Show) Then
                    fileAddress = .SelectedItems.Item(.SelectedItems.Count)
                End If
            
                If fileAddress <> "" Then
                    ActiveSheet.ExportAsFixedFormat _
                    Filename:=fileAddress, _
                    Type:=xlTypePDF, _
                    Quality:=xlQualityStandard, _
                    IncludeDocProperties:=True, _
                    IgnorePrintAreas:=False, _
                    OpenAfterPublish:=True
                End If
                    
            End With
                
        End If
        'Reset Status
        Application.ScreenUpdating = currScr
        Application.Calculation = currCalc
    Else
        MsgBox ("Please Run the Save PDF Code only on the 'Variable Summary' or 'Detailed Results' sheets. Nothing Saved.")
    End If
End Sub

Sub showAllSheets()
    'Shows and Unprotects all Sheets
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    Dim ws As Worksheet
    Dim pw As String
    Dim toUnhide() As String
    Dim toUnprotect() As String
    Dim pwErrorSheets() As String
    Dim note As String
    Dim i As Long: i = 1 'counts unhidden sheets
    Dim j As Long: j = 1 'counts unprotected sheets
    Dim k As Long: k = 1 'counts sheets that could not be unprotected - wrong pw
    pw = InputBox("Please Enter the Password for all Sheets.", "Unhide and Unprotect All Sheets")
    ReDim Preserve toUnhide(1 To 50)
    ReDim Preserve toUnprotect(1 To 50)
    ReDim Preserve pwErrorSheets(1 To 50)
    For Each ws In ActiveWorkbook.Worksheets
        If ws.Visible <> True Then
            toUnhide(i) = ws.Name
            i = i + 1
            ws.Visible = True
        End If
        If ws.ProtectContents Then 'test password
            On Error GoTo wrongPasswordError
            ws.Unprotect (pw)
            On Error GoTo 0
            toUnprotect(j) = ws.Name
            j = j + 1
endofPwErr:
        End If
    Next
        
    If i > 1 Then  'Post a joint message about which sheets altered
        ReDim Preserve toUnhide(1 To i - 1)
        note = note & "The Following Sheets Have Been Unhidden: " & Join(toUnhide, ", ") & "." & Chr(10) & Chr(10)
    End If
    If j > 1 Then 'Post a message about which sheets unprotected
        ReDim Preserve toUnprotect(1 To j - 1)
        note = note & "The Following Sheets Have Been Unprotected: " & Join(toUnprotect, ", ") & "." & Chr(10) & Chr(10)
    End If
    If k > 1 Then 'Message about error password
        ReDim Preserve pwErrorSheets(1 To k - 1)
        note = note & "The Following Sheets Could Not Be Unprotected As the Password Was Incorrect: " & Join(pwErrorSheets, ", ") & "."
    End If
    If Not i > 1 And Not j > 1 And Not k > 1 Then
        MsgBox ("No Sheets to Unhide or Unprotect.")
    Else
        MsgBox note
    End If

    
    Application.ScreenUpdating = True
    Application.Calculation = xlAutomatic
    
    Exit Sub

wrongPasswordError:
            pwErrorSheets(k) = ws.Name
            k = k + 1
            Resume endofPwErr
End Sub


Sub summarizeVariables()
'Summarizes all the statistics of the variables on a Variable Meta-analysis sheet

If Left(ActiveSheet.Name, 22) = "Variable Meta-analysis" Then
    
    'Declare
    Dim foundColumn As Boolean
    Dim FoundCell As Range
    Dim FoundCell2 As Range
    Dim FoundCell3 As Range
    Dim LastCell As Range
    Dim FirstAddr As String
    Dim modelVar As modelVarType
    Dim i As Long
    Dim j As Long
    Dim vars As Long
    Dim stamp As String
    Dim currScr As Long
    Dim currCalc As Long
    
    'Calculates the Payback for every year of analysis
    'Save Status
    currScr = Application.ScreenUpdating
    currCalc = Application.Calculation
    'Deactivate Screen
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    'Dim variableMap(1 To 50, 1 To 2) As String 'Holds the names of variables used on VMA and the equivalent names on Adv Controls
   
    stamp = DatePart("d", DateTime.Now()) & WorksheetFunction.Text(Date, "[$-409]mmm") & DatePart("yyyy", DateTime.Now())

    'Clean out previous Summary
    With Sheets("Variable Summary")
        If .Range("C4").Value > 0 Then
            .Rows(CStr(8) & ":" & CStr(7 + .Range("C4").Value)).Delete
        End If
    End With
    
    'Add new variables
    i = -1
    vars = 0
    foundColumn = False 'Due to sheet edits, and customizations, actual column may be different in different models
    Do While foundColumn <> True
        i = i + 1
        With ActiveSheet.Range("I40:I2000").Offset(0, i)
            Set LastCell = .Cells(.Cells.Count)
            Set FoundCell = .Find(What:="Raw Data Input", After:=LastCell, LookIn:=xlValues, lookat:=xlPart)
            
            If Not FoundCell Is Nothing Then
                foundColumn = True
                FirstAddr = FoundCell.Address
            End If
            Do Until FoundCell Is Nothing
                'Extract the data from the table and related tables
                FoundCell.Select
                Selection.Offset(0, 1 - Selection.Column).Select
                Range(Selection, Selection.End(xlDown)).Select
                j = Selection.Count
                Range(FoundCell.Offset(1, 0), FoundCell.Offset(j - 1, 0)).Select
                If WorksheetFunction.CountA(Selection) > 0 Then 'The table has data
                    vars = vars + 1
                    'Locate the Variable name
                    modelVar.Name = WorksheetFunction.IfError(FoundCell.Offset(0, 1 - FoundCell.Column).End(xlUp).Offset(0, 2).Value, "ERROR: Check Name")
                    'Locate the Variable units
                    Set FoundCell2 = Range(FoundCell, FoundCell.Offset(0, 20)).Find(What:="Units of measure", After:=FoundCell)
                    modelVar.Unit = WorksheetFunction.IfError(FoundCell2.Offset(1, 0).Value, "ERROR: Check Unit")
                    'Find variable statistical data
                    Set FoundCell2 = FoundCell2.Offset(0, -3).End(xlDown)
                    'For the BioSeq models, there is an additional set of results, we adjust for that
                    If Right(FoundCell2.Offset(0, -1).Value, 5) <> "Count" Then 'move upwards one cell
                        Set FoundCell2 = FoundCell2.Offset(-1, 0)
                    End If
                    If FoundCell2.Offset(3, 0).Value = "Y" Then 'Weighted Data are used
                        modelVar.SD = WorksheetFunction.IfError(FoundCell2.Offset(-1, 2).Value, "ERROR: Check Statistics")
                        modelVar.Low = WorksheetFunction.IfError(FoundCell2.Offset(-3, 2).Value, "ERROR: Check Statistics")
                        modelVar.High = WorksheetFunction.IfError(FoundCell2.Offset(-4, 2).Value, "ERROR: Check Statistics")
                        modelVar.Mean = WorksheetFunction.IfError(FoundCell2.Offset(-5, 2).Value, "ERROR: Check Statistics")
                    Else 'Unweighted data used that is stat corrected
                        modelVar.SD = WorksheetFunction.IfError(FoundCell2.Offset(-1, 1).Value, "ERROR: Check Statistics")
                        modelVar.Low = WorksheetFunction.IfError(FoundCell2.Offset(-3, 1).Value, "ERROR: Check Statistics")
                        modelVar.High = WorksheetFunction.IfError(FoundCell2.Offset(-4, 1).Value, "ERROR: Check Statistics")
                        If Not IsError(FoundCell2.Offset(-5, 1).Value) Then 'take stat-corrected mean of Global values
                            modelVar.Mean = FoundCell2.Offset(-5, 1).Value
                        ElseIf Not IsError(FoundCell2.Offset(1, 1).Value) Then 'take stat-corrected sum of regional values
                            modelVar.Mean = FoundCell2.Offset(1, 1).Value
                        ElseIf Not IsError(FoundCell2.Offset(-5, 0).Value) Then 'take mean of global values
                            modelVar.Mean = FoundCell2.Offset(-5, 0).Value
                        ElseIf Not IsError(FoundCell2.Offset(1, 0).Value) Then 'take sum of regional values
                            modelVar.Mean = FoundCell2.Offset(1, 0).Value
                        Else 'All values are in error
                            modelVar.Mean = "ERROR: Check Statistics"
                        End If
                    End If
                    If (Not IsError(FoundCell2.Offset(0, 1).Value) And FoundCell2.Offset(0, 1).Value <> 0) Then 'Take stat-corrected count
                        modelVar.Count = FoundCell2.Offset(0, 1).Value
                    Else
                        modelVar.Count = WorksheetFunction.IfError(FoundCell2.Value, "ERROR: Check Statistics")
                    End If
                    
                    'The only place that the actual value used for this variable is found is on the Advanced Controls, Search there
                    If modelVar.Name = "Current Adoption" Then 'Do a slightly different search
                        Set FoundCell2 = Sheets("Advanced Controls").Range("A1:J300").Find( _
                        What:="Adoption In", LookIn:=xlValues, lookat:=xlWhole)
                        modelVar.Value = WorksheetFunction.IfError(FoundCell2.Offset(1, 0).Address, "ERROR: Check Advanced Controls")
                    ElseIf modelVar.Name = "Sequestration Rates" Then  'Do a slightly different search
                        Set FoundCell2 = Sheets("Advanced Controls").Range("A1:J300").Find( _
                        What:="Sequestration Rate for All Land or All of Special Land", LookIn:=xlValues)
                        modelVar.Value = WorksheetFunction.IfError(FoundCell2.Offset(2, 0).Address, "ERROR: Check Advanced Controls")
                    ElseIf Left(modelVar.Name, 5) <> "ERROR" Then
                        Set FoundCell2 = Sheets("Advanced Controls").Range("A1:J300").Find(What:=modelVar.Name, LookIn:=xlValues)
                        modelVar.Value = WorksheetFunction.IfError(FoundCell2.Offset(2, 0).Address, "ERROR: Check Advanced Controls")
                    Else 'Name is in error
                        modelVar.Value = "ERROR: Name Needed"
                    End If
                
                    'Now save the variable's description on the Variable Summary sheet
                    With Sheets("Variable Summary")
                        .Range("A7").Offset(vars, 0).EntireRow.Insert
                        .Range("A7").EntireRow.Copy (.Range("A7").Offset(vars, 0)) ' Row 7 has all formatting needed but is hidden
                        .Range("A7").Offset(vars, 0).EntireRow.Hidden = False ' This new row would also be hidden at first
                        .Range("A7").Offset(vars, 1).Value = modelVar.Name
                        .Range("A7").Offset(vars, 2).Value = modelVar.Unit
                        If Left(modelVar.Value, 5) <> "ERROR" Then 'Add a formula so that value updates automatically
                            .Range("A7").Offset(vars, 3).Formula = "='Advanced Controls'!" + CStr(modelVar.Value)
                        Else 'Add error message
                            .Range("A7").Offset(vars, 3).Value = modelVar.Value
                        End If
                        .Range("A7").Offset(vars, 4).Value = modelVar.Mean
                        .Range("A7").Offset(vars, 5).Value = modelVar.SD
                        .Range("A7").Offset(vars, 6).Value = modelVar.Low
                        .Range("A7").Offset(vars, 7).Value = modelVar.High
                        .Range("A7").Offset(vars, 8).Value = modelVar.Count
                    End With
                    
                    'If Sequestration Rates are being examined, then we want to expand the detail to the several thermal regimes
                    If modelVar.Name = "Sequestration Rates" Then
                        Set FoundCell2 = FoundCell.Offset(-1, 33)
                        For k = 1 To 5 ' For each Thermal Regime
                            Set FoundCell2 = FoundCell2.Offset(0, 3) 'find next Thermal Regime Summary Table
                            If FoundCell2.Offset(1, 1).End(xlDown).End(xlDown).End(xlDown).Value > 0 Then 'This regime has data
                                vars = vars + 1
                                modelVar.Name = FoundCell2.Value & " Sequestration Rate"
                                'Unit is the same, no change
                                modelVar.Count = FoundCell2.Offset(1, 1).End(xlDown).End(xlDown).End(xlDown).Value
                                modelVar.SD = FoundCell2.Offset(1, 1).End(xlDown).End(xlDown).Offset(1, 0).Value
                                modelVar.Low = FoundCell2.Offset(1, 1).End(xlDown).Value
                                modelVar.High = FoundCell2.Offset(1, 1).End(xlDown).Offset(-1, 0).Value
                                modelVar.Mean = FoundCell2.Offset(1, 1).End(xlDown).Offset(-2, 0).Value
                                'The only place that the actual value used for this variable is found is on the Advanced Controls, Search there
                                Set FoundCell3 = Sheets("Advanced Controls").Range("A1:J300").Find(What:=modelVar.Name, LookIn:=xlValues)
                                modelVar.Value = FoundCell3.Offset(2, 0).Address
                                'Now save the variable's description on the Variable Summary sheet
                                With Sheets("Variable Summary")
                                    .Range("A7").Offset(vars, 0).EntireRow.Insert
                                    .Range("A7").EntireRow.Copy (.Range("A7").Offset(vars, 0)) ' Row 7 has all formatting needed but is hidden
                                    .Range("A7").Offset(vars, 0).EntireRow.Hidden = False ' This new row would also be hidden at first
                                    .Range("A7").Offset(vars, 1).Value = modelVar.Name
                                    .Range("A7").Offset(vars, 2).Value = modelVar.Unit
                                    If Left(modelVar.Value, 5) <> "ERROR" Then 'Add a formula so that value updates automatically
                                        .Range("A7").Offset(vars, 3).Formula = "='Advanced Controls'!" + CStr(modelVar.Value)
                                    Else 'Add Error message
                                        .Range("A7").Offset(vars, 3).Value = modelVar.Value
                                    End If
                                    .Range("A7").Offset(vars, 4).Value = modelVar.Mean
                                    .Range("A7").Offset(vars, 5).Value = modelVar.SD
                                    .Range("A7").Offset(vars, 6).Value = modelVar.Low
                                    .Range("A7").Offset(vars, 7).Value = modelVar.High
                                    .Range("A7").Offset(vars, 8).Value = modelVar.Count
                                End With
                            End If
                        Next
                    End If
                End If
                Set FoundCell = ActiveSheet.Range("I40:I2000").Offset(0, i).Find(What:="Raw Data Input", _
                After:=FoundCell, LookIn:=xlValues, lookat:=xlPart)
                If FoundCell.Address = FirstAddr Then
                    Exit Do
                End If
            Loop
        End With
    Loop
    
    Sheets("Variable Summary").Range("h3").Value = stamp
    Sheets("Variable Summary").Range("c4").Value = vars
    Sheets("Variable Summary").Activate
    Application.Calculate
    'Reset Screen
    Application.ScreenUpdating = currScr
    Application.Calculation = currCalc
Else 'Macro called from some non VMA sheet
    MsgBox ("Please Run the SummarizeVariable Macro on a Variable Meta-analysis Sheet Only. It will Summarize the Variables on that sheet. Macro is Cancelled.")
End If
End Sub
Sub switchVMAValidationtoVMA()
    Call switchVMAValidation
End Sub

Sub switchVMAValidationtoVMAO()
    Call switchVMAValidation("Variable Meta-analysis-Open")
End Sub

Sub switchVMAValidation(Optional ByVal destinSheet As String = "Variable Meta-analysis")
    
    
    Dim nameR As Range: Dim sourceR As Range: Dim dropdownR As Range
    Dim counter As Long
    Dim rowRef As Variant
    Dim noMoreVars As Boolean
    Dim CurrCell As Range
    Dim LastCell As Range
    Dim FoundCell As Range
    Dim varName As String
    Dim addrDropdown As String
    Dim addrSources As String
    Dim dropdownFmla As String
    Dim sourcesFmla As String
    Dim variableRows() As String: Dim variableRowsAgri() As String: Dim variableRowsBioSeq() As String
    Dim variableRowsProtect() As String: Dim variableRowsRRS() As String: Dim variableRowsEnergySol() As String
    Dim failedVars() As String
    ReDim Preserve failedVars(1 To 50)
    Dim i As Long: i = 0
    Dim currScr As Long
    Dim currCalc As Long
    Dim dataCol As Long
        
    'Save Status
    currScr = Application.ScreenUpdating
    currCalc = Application.Calculation
    'Deactivate
    Application.ScreenUpdating = False
    Application.Calculation = xlManual
    
    'Save all references for rows with variables names for all different models
    variableRowsAgri = Split("A75," & "A90," & "A121," & "A136," & "A171," & "A203," & "A217", ",")
    variableRowsBioSeq = Split("A75," & "A90," & "A121," & "A136," & "A171," & "A203," & "A217", ",")
    variableRowsProtect = Split("A75," & "A90," & "A121," & "A136," & "A171," & "A185," & "A217," & "A231", ",")
    variableRowsRRS = Split("A96," & "A111," & "A142," & "A157," & "A190," & "A205", ",")
    variableRowsEnergySol = Split("A93," & "A109," & "A126," & "A157," & "A172," & "A205," & "A220", ",")
    
    'Determine which set of rows to use for this model
    Select Case Sheets("Welcome").Range("I1").Value
    Case "BioS.Agri"
        variableRows = variableRowsAgri
        dataCol = 18
    Case "BioS"
        variableRows = variableRowsBioSeq
        dataCol = 18
    Case "BioS.Prot"
        variableRows = variableRowsProtect
        dataCol = 18
    Case "RRS"
        variableRows = variableRowsRRS
        dataCol = 17
    Case "RRS.ES"
        variableRows = variableRowsEnergySol
        dataCol = 17
    End Select
        
    For Each rowRef In variableRows
    'For each cell in variableRows, all variables in row will be adjusted
        Set CurrCell = Sheets("Advanced Controls").Range(rowRef) 'Go to Column A to Start
        
        noMoreVars = False ' Reset for this row
        Do Until noMoreVars ' inthis row
            counter = 0 'Reset for this variable search
            Sheets("Advanced Controls").Activate
            Set CurrCell = CurrCell.Offset(0, 1)
            Set nameR = Range(CurrCell.Address) 'this is a variable name hopefully
            varName = nameR.Value 'We need to search for this on destinSheet
            
            If varName <> "" Then
                If Left(varName, 18) = "Sequestration Rate" Or Right(varName, 18) = "Sequestration Rate" Then
                    varName = "Sequestration Rates"
                    'All Sequestration Dropdown boxes will be the same
                End If
                
                Set dropdownR = nameR(1, 1).Offset(1, 0)
            
                Do While CStr(dropdownR.Value) <> "Project Drawdown Data" And counter < 10
                    Set dropdownR = dropdownR.Offset(1, 0)
                    counter = counter + 1
                Loop
                If counter < 10 Then
                    Set dropdownR = dropdownR.Offset(7, 0) ' This is the dropdown box
                    Set sourceR = dropdownR.Offset(1, 0) ' This is the Sources box
                    
                    With Sheets(destinSheet).Range("C40:C2000")
                        Set LastCell = .Cells(.Cells.Count)
                        Set FoundCell = .Find(What:=varName, After:=LastCell, LookIn:=xlValues, lookat:=xlPart)
                        If Not (FoundCell Is Nothing) Then
                            'Extract the data from the table
                            Sheets(destinSheet).Activate
                            FoundCell.Select
                            Selection.Offset(0, 1 - Selection.Column).Select
                            Do While Selection.Value <> "Number"
                                Selection.Offset(1, 0).Select
                            Loop
                
                            Range(Selection, Selection.End(xlDown)).Offset(0, 1).Select 'This is our (hidden) target range
                            addrDropdown = Selection.Address
                            addrSources = Range(Selection, Selection.Offset(0, 20)).Address
                            dropdownFmla = "='" + destinSheet + "'!" + addrDropdown
                            sourcesFmla = "=VLOOKUP(" + dropdownR.Address + ",'" + destinSheet + "'!" + addrSources + "," + CStr(dataCol) + ",FALSE)"
                            
                            'Adjust Dropdown cell's validation formula
                            With dropdownR.Validation
                                .Delete
                                .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Operator:= _
                                    xlBetween, Formula1:=dropdownFmla
                            End With
                            'Adjust Sources cell formula
                            sourceR.Formula = sourcesFmla
                        Else
                            i = i + 1
                            failedVars(i) = nameR.Value
                        End If
                            
                    End With
                Else
                    i = i + 1
                    failedVars(i) = nameR.Value
                End If
            Else 'See if all relevant Columns checked: all Variables in this row have been Switched?
                If nameR.Column > 10 Then
                    noMoreVars = True
                End If
            End If
        Loop
    Next rowRef
        
    ReDim Preserve failedVars(1 To i)
    MsgBox ("The Following Variables had Errors when Switching Source Dropdowns from VMA to VMA-Open: " & Chr(10) & Join(failedVars, ", " & Chr(10)) & "." & Chr(10) & Chr(10))
     
    Sheets("Advanced Controls").Activate
     'Reset status
    Application.ScreenUpdating = currScr
    Application.Calculation = currCalc
End Sub
