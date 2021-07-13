' For each scenario, generate CSVs for all pages
' Used to create static results for testing python code


Function Should_Export(sht) As Boolean
    ' Sheets that we need to save, which are sheets that contain core calculations and outputs
    ' that we might want to test.  If this is not a standard RSS/Land solution, you should
    ' check that the list is appropriate
    Dim skip_sheets As Variant
    export_sheets = Array("Advanced Controls", "ScenarioRecord", "Variable Meta-Analysis", _
                          "TAM Data", "TLA Data", "AEZ Data", _
                          "Adoption Data", "Custom PDS Adoption", "Custom REF Adoption", "S-Curve Adoption", _
                          "Helper Tables", "Unit Adoption Calculations", _
                          "First Cost", "Operating Cost", "Net Profit Margin", _
                          "Emissions Factors", "CO2 Calcs", "CH4 Calcs")
    Should_Export = False
    For Each keep In export_sheets
        If sht = keep Then
            Should_Export = True
            Exit Function
        End If
    Next
End Function

Function Get_Index_Sheet() As Worksheet
    ' Get or create Index Sheet
    Dim x As Worksheet
    On Error Resume Next
    Set x = Sheets("Export Tracking")
    On Error GoTo 0
    If x Is Nothing Then
        Set x = Sheets.Add
        x.Name = "Export Tracking"
    End If
    x.Cells.Clear
    Set Get_Index_Sheet = x
End Function


Sub Save_Sheet_As_CSV(sheetname As String, filename As String)
    ' Make a CSV file for sheet in the same directory as the current workbook
    ' To save a single sheet without affecting the current workbook, we make a new
    ' workbook, copy the sheet to it, save that workbook, then close it.
    
    Application.ScreenUpdating = False

    Dim dir As String
    Dim sht As Worksheet
    Dim tmpbook As Workbook
    
    dir = ActiveWorkbook.Path
    Set sht = Sheets(sheetname)
    Set tmpbook = Workbooks.Add
    outname = dir & Application.PathSeparator & filename
    
    ' Activate the original sheet to make sure any activation macros have run (Detailed Results does some)
    sht.Activate
    ' Copy over the Cells (not the Sheet) so that we don't get any of that pesky macro stuff.
    sht.Cells.Copy
    tmpbook.Sheets(1).Cells.PasteSpecial Paste:=xlPasteValues

    ' Save the temporary workbook, suppressing "Do you want to overwrite" dialog
    Application.DisplayAlerts = False
    tmpbook.SaveAs filename:=outname, FileFormat:=xlCSVUTF8
    Application.DisplayAlerts = True

    ' Bye bye
    tmpbook.Close
    Application.ScreenUpdating = True
End Sub

Sub test_save_sheet()
    Call Save_Sheet_As_CSV("Detailed Results", "testout.csv")
End Sub

' This is the main macro.  Run this to save all sheets for all scenarios.

Sub Generate_Scenario_Records()
    Dim scenario_list As Range
    Set scenario_list = Range("ScenarioRecord!$AR$13:$AR$92").Cells
    
    ' temporary index of filenames
    Dim index_sheet As Worksheet
    Set index_sheet = Get_Index_Sheet()

    counter = 0
    basename = ActiveWorkbook.Name
    Dim fname As String
    
    For Each scenario In scenario_list
        If scenario <> "" Then
            
            ' Load the scenario
            Sheets("ScenarioRecord").Activate
            Range("$B$9").Value = scenario
            Call LoadScenario_Click
            
            ' Write out the sheets
            For Each x In Worksheets
                If Should_Export(x.Name) Then
                    counter = counter + 1
                    fname = basename & "_" & counter & ".csv"
                    
                    Call Save_Sheet_As_CSV(x.Name, fname)
                    
                    ' Add to index
                    index_sheet.Cells(counter, 1) = fname
                    index_sheet.Cells(counter, 2) = scenario
                    index_sheet.Cells(counter, 3) = x.Name
                End If
            Next
        End If
    Next
    
    ' Write out the index file
    fname = ActiveWorkbook.Name & "_index.csv"
    Call Save_Sheet_As_CSV(index_sheet.Name, fname)
    ' Delete tracking sheet, suppressing Delete Sheet warning
    Application.DisplayAlerts = False
    index_sheet.Delete
    Application.DisplayAlerts = True
End Sub


