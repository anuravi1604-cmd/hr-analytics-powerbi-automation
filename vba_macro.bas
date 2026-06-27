Attribute VB_Name = "HRAntiatrionAutomation"
' ==============================================================================
' Module: HR Attrition Automation & Validation
' Purpose: Automates data entry validation and master database exports
'          for the Enterprise HR Analytics system.
' Author: HR People Analytics Team
' ==============================================================================

Option Explicit

Sub ValidateAndExportEmployee()
    ' Variables for Sheet and Row Mapping
    Dim wsInput As Worksheet
    Dim lastRow As Long
    Dim empId As String
    Dim age As Integer
    Dim gender As String
    Dim dept As String
    Dim role As String
    Dim salary As Double
    Dim overtime As String
    Dim jobSat As Integer
    Dim envSat As Integer
    Dim wlb As Integer
    Dim perfRating As Integer
    Dim attrition As String
    
    Dim isValid As Boolean
    isValid = True
    
    ' Set reference to worksheet
    Set wsInput = ThisWorkbook.Sheets("Data_Entry_Form")
    
    ' Retrieve values from specific cells (assuming a structured form layout)
    ' In a production sheet, these are named ranges or form controls
    empId = Trim(wsInput.Range("C4").Value)        ' Employee ID
    age = Val(wsInput.Range("C5").Value)          ' Age
    gender = Trim(wsInput.Range("C6").Value)       ' Gender (Male, Female, Non-binary)
    dept = Trim(wsInput.Range("C7").Value)         ' Department
    role = Trim(wsInput.Range("C8").Value)         ' Job Role
    salary = Val(wsInput.Range("C9").Value)        ' Annual Salary
    overtime = Trim(wsInput.Range("C10").Value)    ' Overtime (Yes, No)
    jobSat = Val(wsInput.Range("C11").Value)       ' Job Satisfaction (1-5)
    envSat = Val(wsInput.Range("C12").Value)       ' Environment Satisfaction (1-5)
    wlb = Val(wsInput.Range("C13").Value)          ' Work Life Balance (1-5)
    perfRating = Val(wsInput.Range("C14").Value)   ' Performance Rating (1-4)
    attrition = Trim(wsInput.Range("C15").Value)    ' Attrition (Yes, No)
    
    ' ==========================================
    ' DATA VALIDATION LOGIC
    ' ==========================================
    Dim errorMsg As String
    errorMsg = "Data Validation Errors Found:" & vbCrLf
    
    ' Validate Employee ID (Format: EMP####)
    If Not empId Like "EMP####" Then
        isValid = False
        errorMsg = errorMsg & "- Employee ID must be in the format 'EMP' followed by 4 digits (e.g. EMP1234)." & vbCrLf
    End If
    
    ' Validate Age
    If age < 18 Or age > 70 Then
        isValid = False
        errorMsg = errorMsg & "- Age must be between 18 and 70." & vbCrLf
    End If
    
    ' Validate Gender
    If gender <> "Male" And gender <> "Female" And gender <> "Non-binary" Then
        isValid = False
        errorMsg = errorMsg & "- Gender must be 'Male', 'Female', or 'Non-binary'." & vbCrLf
    End If
    
    ' Validate Overtime
    If overtime <> "Yes" And overtime <> "No" Then
        isValid = False
        errorMsg = errorMsg & "- Overtime must be 'Yes' or 'No'." & vbCrLf
    End If
    
    ' Validate Satisfaction Ratings (1 to 5)
    If jobSat < 1 Or jobSat > 5 Then
        isValid = False
        errorMsg = errorMsg & "- Job Satisfaction must be an integer between 1 and 5." & vbCrLf
    End If
    If envSat < 1 Or envSat > 5 Then
        isValid = False
        errorMsg = errorMsg & "- Environment Satisfaction must be an integer between 1 and 5." & vbCrLf
    End If
    If wlb < 1 Or wlb > 5 Then
        isValid = False
        errorMsg = errorMsg & "- Work-Life Balance must be an integer between 1 and 5." & vbCrLf
    End If
    
    ' Validate Performance Rating (1 to 4)
    If perfRating < 1 Or perfRating > 4 Then
        isValid = False
        errorMsg = errorMsg & "- Performance Rating must be between 1 and 4." & vbCrLf
    End If
    
    ' Validate Attrition Status
    If attrition <> "Yes" And attrition <> "No" Then
        isValid = False
        errorMsg = errorMsg & "- Attrition status must be 'Yes' or 'No'." & vbCrLf
    End If
    
    ' Validate Salary
    If salary <= 0 Then
        isValid = False
        errorMsg = errorMsg & "- Annual Salary must be a positive numeric value." & vbCrLf
    End If

    ' ==========================================
    ' SUBMISSION / EXPORT LOGIC
    ' ==========================================
    If Not isValid Then
        ' Display Validation Errors
        MsgBox errorMsg, vbCritical, "Validation Failure"
        Exit Sub
    End If
    
    ' Save path for CSV file (placed in same directory as Workbook)
    Dim csvPath As String
    Dim fileNum As Integer
    Dim csvLine As String
    
    csvPath = ThisWorkbook.Path & "\weekly_hr_updates.csv"
    
    ' Create CSV format string
    ' Employee_ID, Age, Gender, Department, Job_Role, Annual_Salary, Overtime, Job_Satisfaction, Env_Satisfaction, Work_Life_Balance, Performance_Rating, Attrition
    csvLine = empId & "," & age & "," & gender & "," & dept & "," & role & "," & _
              salary & "," & overtime & "," & jobSat & "," & envSat & "," & _
              wlb & "," & perfRating & "," & attrition
              
    ' Append record to CSV
    fileNum = FreeFile
    
    ' Check if file exists, write header if new file
    Dim fileExists As Boolean
    fileExists = (Len(Dir(csvPath)) > 0)
    
    Open csvPath For Append As #fileNum
    
    If Not fileExists Then
        Print #fileNum, "Employee_ID,Age,Gender,Department,Job_Role,Annual_Salary,Overtime,Job_Satisfaction,Environment_Satisfaction,Work_Life_Balance,Performance_Rating,Attrition"
    End If
    
    Print #fileNum, csvLine
    Close #fileNum
    
    ' Add to local Excel database sheet as backup
    Dim wsDb As Worksheet
    Dim nextRow As Long
    Set wsDb = ThisWorkbook.Sheets("Database_Backup")
    nextRow = wsDb.Cells(wsDb.Rows.Count, 1).End(xlUp).Row + 1
    
    wsDb.Cells(nextRow, 1).Value = empId
    wsDb.Cells(nextRow, 2).Value = age
    wsDb.Cells(nextRow, 3).Value = gender
    wsDb.Cells(nextRow, 4).Value = dept
    wsDb.Cells(nextRow, 5).Value = role
    wsDb.Cells(nextRow, 6).Value = salary
    wsDb.Cells(nextRow, 7).Value = overtime
    wsDb.Cells(nextRow, 8).Value = jobSat
    wsDb.Cells(nextRow, 9).Value = envSat
    wsDb.Cells(nextRow, 10).Value = wlb
    wsDb.Cells(nextRow, 11).Value = perfRating
    wsDb.Cells(nextRow, 12).Value = attrition
    wsDb.Cells(nextRow, 13).Value = Now ' Date submitted
    
    ' Success notification
    MsgBox "Employee " & empId & " successfully validated and exported to weekly update files!", vbInformation, "Submission Successful"
    
    ' Clean the form
    Call ClearForm(wsInput)
End Sub

Sub ClearForm(ws As Worksheet)
    ' Clears input cells on form, setting standard defaults
    On Error Resume Next
    Application.ScreenUpdating = False
    
    ws.Range("C4").Value = ""         ' Clear ID
    ws.Range("C5").Value = ""         ' Clear Age
    ws.Range("C6").Value = "Male"     ' Reset Gender default
    ws.Range("C7").Value = "Technology" ' Reset Dept default
    ws.Range("C8").Value = ""         ' Clear Role
    ws.Range("C9").Value = 0          ' Clear Salary
    ws.Range("C10").Value = "No"      ' Reset Overtime default
    ws.Range("C11").Value = 3         ' Reset JobSat default (neutral)
    ws.Range("C12").Value = 3         ' Reset EnvSat default (neutral)
    ws.Range("C13").Value = 3         ' Reset WLB default (neutral)
    ws.Range("C14").Value = 2         ' Reset Perf default (meets expectations)
    ws.Range("C15").Value = "No"      ' Reset Attrition default
    
    Application.ScreenUpdating = True
End Sub
