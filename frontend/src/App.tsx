import { Navigate, Route, Routes } from "react-router-dom";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { Dashboard } from "./pages/Dashboard";
import { Events } from "./pages/Events";
export default function App() { return <DashboardLayout><Routes><Route path="/" element={<Navigate to="/dashboard" replace/>}/><Route path="/dashboard" element={<Dashboard/>}/><Route path="/events" element={<Events/>}/><Route path="*" element={<Navigate to="/dashboard" replace/>}/></Routes></DashboardLayout>; }
