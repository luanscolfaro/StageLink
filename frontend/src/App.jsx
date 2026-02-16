import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import ProtectedRoute from "./components/ProtectedRoute";
import FeedPage from "./pages/FeedPage";
import GigsPage from "./pages/GigsPage";
import ProfilePage from "./pages/ProfilePage";
import Register from "./pages/Register";
import SearchPeople from "./pages/SearchPeople";
import MeRedirect from "./pages/MeRedirect";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/register" element={<Register />} />


        <Route
          path="/feed"
          element={
            <ProtectedRoute>
              <FeedPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/gigs"
          element={
            <ProtectedRoute>
              <GigsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/feed" replace />} />
        <Route path="/people" element={<SearchPeople />} />
        <Route path="/profile/:username" element={<ProfilePage />} />
        <Route path="/me" element={<MeRedirect />} />


      </Routes>
    </BrowserRouter>
  );
}
