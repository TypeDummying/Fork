
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

namespace Fork.CrashHandling
{
    /// <summary>
    /// Handles crashes and unexpected exceptions in the Fork 3D modeling software.
    /// This class provides comprehensive crash handling, logging, and recovery mechanisms.
    /// </summary>
    public class CrashHandler
    {
        // Constants for file paths and settings
        private const string LOG_DIRECTORY = @"C:\ProgramData\Fork\CrashLogs";
        private const string CRASH_REPORT_FILE = "CrashReport_{0}.txt";
        private const int MAX_CRASH_LOGS = 50;
        private const int CRASH_REPORT_RETENTION_DAYS = 30;

        // Delegate for custom error handling
        public delegate void CustomErrorHandler(Exception ex);

        // Event for custom error handling
        public static event CustomErrorHandler OnCustomErrorHandler;

        /// <summary>
        /// Initializes the crash handler and sets up global exception handling.
        /// </summary>
        public static void Initialize()
        {
            AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;
            Application.ThreadException += OnThreadException;
            Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);

            // Ensure log directory exists
            if (!Directory.Exists(LOG_DIRECTORY))
            {
                Directory.CreateDirectory(LOG_DIRECTORY);
            }

            CleanupOldCrashLogs();
        }

        /// <summary>
        /// Handles unhandled exceptions at the AppDomain level.
        /// </summary>
        /// <param name="sender">The source of the unhandled exception.</param>
        /// <param name="e">Contains information about the exception.</param>
        private static void OnUnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            Exception ex = (Exception)e.ExceptionObject;
            HandleCrash(ex, "Unhandled AppDomain Exception");
        }

        /// <summary>
        /// Handles unhandled exceptions in Windows Forms threads.
        /// </summary>
        /// <param name="sender">The source of the thread exception.</param>
        /// <param name="e">Contains information about the exception.</param>
        private static void OnThreadException(object sender, ThreadExceptionEventArgs e)
        {
            HandleCrash(e.Exception, "Unhandled Thread Exception");
        }

        /// <summary>
        /// Main method to handle crashes, log information, and perform recovery actions.
        /// </summary>
        /// <param name="ex">The exception that caused the crash.</param>
        /// <param name="source">The source of the exception (e.g., "Unhandled Thread Exception").</param>
        private static void HandleCrash(Exception ex, string source)
        {
            try
            {
                // Log the crash
                string crashReport = GenerateCrashReport(ex, source);
                string fileName = string.Format(CRASH_REPORT_FILE, DateTime.Now.ToString("yyyyMMdd_HHmmss"));
                string fullPath = Path.Combine(LOG_DIRECTORY, fileName);
                File.WriteAllText(fullPath, crashReport);

                // Invoke custom error handler if set
                OnCustomErrorHandler?.Invoke(ex);

                // Attempt to save user's work
                AttemptToSaveUserWork();

                // Display error message to the user
                ShowErrorMessage(ex);

                // Perform cleanup and prepare for restart
                CleanupAndPrepareForRestart();

                // Restart the application
                RestartApplication();
            }
            catch (Exception handlerEx)
            {
                // If crash handling itself fails, log to Windows Event Log
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Critical error in crash handler: {handlerEx.Message}\n\nOriginal error: {ex.Message}", 
                    EventLogEntryType.Error);
            }
        }

        /// <summary>
        /// Generates a detailed crash report.
        /// </summary>
        /// <param name="ex">The exception that caused the crash.</param>
        /// <param name="source">The source of the exception.</param>
        /// <returns>A string containing the crash report.</returns>
        private static string GenerateCrashReport(Exception ex, string source)
        {
            StringWriter sw = new StringWriter();
            sw.WriteLine("Fork 3D Modeling Software - Crash Report");
            sw.WriteLine("========================================");
            sw.WriteLine($"Timestamp: {DateTime.Now}");
            sw.WriteLine($"Source: {source}");
            sw.WriteLine($"Exception Type: {ex.GetType().FullName}");
            sw.WriteLine($"Message: {ex.Message}");
            sw.WriteLine($"Stack Trace:");
            sw.WriteLine(ex.StackTrace);
            sw.WriteLine("\nSystem Information:");
            sw.WriteLine($"Operating System: {Environment.OSVersion}");
            sw.WriteLine($"64-bit Operating System: {Environment.Is64BitOperatingSystem}");
            sw.WriteLine($"Machine Name: {Environment.MachineName}");
            sw.WriteLine($"User Name: {Environment.UserName}");
            sw.WriteLine($"CLR Version: {Environment.Version}");
            sw.WriteLine($"Working Set: {Environment.WorkingSet} bytes");

            // Include information about loaded modules
            sw.WriteLine("\nLoaded Modules:");
            foreach (ProcessModule module in Process.GetCurrentProcess().Modules)
            {
                sw.WriteLine($"{module.ModuleName}: {module.FileName}");
            }

            return sw.ToString();
        }

        /// <summary>
        /// Attempts to save the user's current work to prevent data loss.
        /// </summary>
        private static void AttemptToSaveUserWork()
        {
            try
            {
                // TODO: Implement auto-save functionality
                // This could involve serializing the current model state to a temporary file
                // Example:
                // ModelSerializer.SaveToTempFile(CurrentModel);
            }
            catch (Exception saveEx)
            {
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Failed to auto-save user work: {saveEx.Message}", 
                    EventLogEntryType.Warning);
            }
        }

        /// <summary>
        /// Displays an error message to the user.
        /// </summary>
        /// <param name="ex">The exception to display information about.</param>
        private static void ShowErrorMessage(Exception ex)
        {
            string message = $"We apologize, but Fork 3D Modeling Software has encountered an unexpected error and needs to restart.\n\n" +
                             $"Error details: {ex.Message}\n\n" +
                             "A crash report has been generated and will be sent to our development team for analysis.\n\n" +
                             "The application will now attempt to restart.";

            MessageBox.Show(message, "Fork 3D Modeling Software - Unexpected Error", 
                MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

        /// <summary>
        /// Performs cleanup operations and prepares the application for a restart.
        /// </summary>
        private static void CleanupAndPrepareForRestart()
        {
            try
            {
                // TODO: Implement cleanup logic
                // This could involve releasing system resources, closing file handles, etc.
                // Example:
                // ReleaseSystemResources();
                // CloseOpenFileHandles();
            }
            catch (Exception cleanupEx)
            {
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Error during cleanup before restart: {cleanupEx.Message}", 
                    EventLogEntryType.Warning);
            }
        }

        /// <summary>
        /// Restarts the application.
        /// </summary>
        private static void RestartApplication()
        {
            string appPath = Application.ExecutablePath;
            Process.Start(appPath);
            Environment.Exit(1);
        }

        /// <summary>
        /// Cleans up old crash logs to manage disk space.
        /// </summary>
        private static void CleanupOldCrashLogs()
        {
            try
            {
                var directory = new DirectoryInfo(LOG_DIRECTORY);
                var files = directory.GetFiles(string.Format(CRASH_REPORT_FILE, "*"));

                // Delete old files if we have more than the maximum allowed
                if (files.Length > MAX_CRASH_LOGS)
                {
                    Array.Sort(files, (x, y) => y.CreationTime.CompareTo(x.CreationTime));
                    for (int i = MAX_CRASH_LOGS; i < files.Length; i++)
                    {
                        files[i].Delete();
                    }
                }

                // Delete files older than the retention period
                var cutoffDate = DateTime.Now.AddDays(-CRASH_REPORT_RETENTION_DAYS);
                foreach (var file in files)
                {
                    if (file.CreationTime < cutoffDate)
                    {
                        file.Delete();
                    }
                }
            }
            catch (Exception ex)
            {
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Error cleaning up old crash logs: {ex.Message}", 
                    EventLogEntryType.Warning);
            }
        }

        /// <summary>
        /// Checks if the application is running with administrator privileges.
        /// </summary>
        /// <returns>True if the application is running as administrator, false otherwise.</returns>
        private static bool IsRunningAsAdministrator()
        {
            WindowsIdentity identity = WindowsIdentity.GetCurrent();
            WindowsPrincipal principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }

        /// <summary>
        /// Attempts to create a memory dump of the application for advanced debugging.
        /// </summary>
        private static void CreateMemoryDump()
        {
            if (!IsRunningAsAdministrator())
            {
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    "Cannot create memory dump: Application is not running as administrator.", 
                    EventLogEntryType.Warning);
                return;
            }

            try
            {
                string dumpFileName = Path.Combine(LOG_DIRECTORY, $"MemoryDump_{DateTime.Now:yyyyMMdd_HHmmss}.dmp");
                using (FileStream fs = new FileStream(dumpFileName, FileMode.Create, FileAccess.ReadWrite, FileShare.Write))
                {
                    MiniDumpWriteDump(Process.GetCurrentProcess().Handle, 
                        (uint)Process.GetCurrentProcess().Id, 
                        fs.SafeFileHandle.DangerousGetHandle(), 
                        MINIDUMP_TYPE.MiniDumpWithFullMemory, 
                        IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
                }

                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Memory dump created successfully: {dumpFileName}", 
                    EventLogEntryType.Information);
            }
            catch (Exception ex)
            {
                EventLog.WriteEntry("Fork 3D Modeling Software", 
                    $"Failed to create memory dump: {ex.Message}", 
                    EventLogEntryType.Error);
            }
        }

        // P/Invoke for creating memory dumps
        [DllImport("dbghelp.dll", EntryPoint = "MiniDumpWriteDump", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
        private static extern bool MiniDumpWriteDump(IntPtr hProcess, uint processId, IntPtr hFile, MINIDUMP_TYPE dumpType, IntPtr exceptionParam, IntPtr userStreamParam, IntPtr callbackParam);

        private enum MINIDUMP_TYPE
        {
            MiniDumpWithFullMemory = 0x00000002
        }
    }
}
