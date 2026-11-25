import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import CoursesPage from "./pages/CoursesPage";
import CourseDetailPage from "./pages/CourseDetailPage";
import BatchesPage from "./pages/BatchesPage";
import LecturesPage from "./pages/LecturesPage";
import AssignmentsPage from "./pages/AssignmentsPage";
import QuizzesPage from "./pages/QuizzesPage";
import AttendancePage from "./pages/AttendancePage";
import PaymentsPage from "./pages/PaymentsPage";
import CertificatesPage from "./pages/CertificatesPage";
import UsersPage from "./pages/UsersPage";
import ReportsPage from "./pages/ReportsPage";
import NotificationsPage from "./pages/NotificationsPage";
import ProfilePage from "./pages/ProfilePage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="courses" element={<CoursesPage />} />
            <Route path="courses/:id" element={<CourseDetailPage />} />
            <Route path="batches" element={<BatchesPage />} />
            <Route path="lectures" element={<LecturesPage />} />
            <Route path="assignments" element={<AssignmentsPage />} />
            <Route path="quizzes" element={<QuizzesPage />} />
            <Route path="attendance" element={<AttendancePage />} />
            <Route path="payments" element={<PaymentsPage />} />
            <Route path="certificates" element={<CertificatesPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
