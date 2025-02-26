import win32print

# Field names for PRINTER_INFO_2 (level 2)
fields = [
    "Flags", "pPrinterName", "pServerName", "pShareName", "pPortName",
    "pDriverName", "pComment", "pLocation", "pDevMode", "pSepFile",
    "pPrintProcessor", "pDatatype", "pParameters", "pSecurityDescriptor",
    "Attributes", "Priority", "DefaultPriority", "StartTime", "UntilTime",
    "Status", "cJobs", "AveragePPM"
]

printers = win32print.EnumPrinters(2)
for printer in printers:
    printer_dict = dict(zip(fields, printer))
    name = printer_dict["pPrinterName"]
    port = printer_dict["pPortName"]
    if "ipp" in port.lower():
        print(f"IPP Printer: {name}, Port: {port}")
    else:
        print(f"Printer: {name}, Port: {port}")