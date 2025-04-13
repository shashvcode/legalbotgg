import React from 'react';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import UserForm from './UserForm';
import './App.css';

const router = createBrowserRouter([
  {
    path: "/",
    element: <UserForm />,
  },
  {
    path: "/chat",
    element: <UserForm />,
  },
  {
    path: "*",
    element: <UserForm />,
  }
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
});

function App() {
  return <RouterProvider router={router} />;
}

export default App;