import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = sessionStorage.getItem("authToken");
    if (!token) {
      navigate("/login");
      return;
    }

    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/profile`, {
      headers: {
        Authorization: `Bearer ${JSON.parse(token).token}`,
      },
    })
      .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then(data => setUser(data.user))
      .catch(() => navigate("/login"));
  }, []);

  if (!user) return <p className="text-center mt-5">Cargando perfil...</p>;

  return (
    <div className="container mt-5">
      <h2>Bienvenido, {user.email}</h2>
      <p>ID: {user.id}</p>
      <p>Activo: {user.is_active ? "Sí" : "No"}</p>
    </div>
  );
};

export default Profile;