import { Navigate } from "react-router-dom";
import { isLogged } from "../auth/auth";

export default function ProtectedRoute({ children }) {
  if (!isLogged()) return <Navigate to="/" replace />;
  return children;
}
