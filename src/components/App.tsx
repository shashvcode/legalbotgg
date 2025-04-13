import React from 'react';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import UserForm from './components/UserForm';
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
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;