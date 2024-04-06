import React, { useContext, useEffect } from 'react'
import Header from '../components/Header/Header';
import AdoptionSection from '../components/AdoptionSection/AdoptionSection';
import ProtectorasSection from '../components/ProtectorasSection/ProtectorasSection';
import Footer from '../components/Footer/Footer';
import { AdminContext } from '../context/admin';
import { USERS } from '../../utils/constants';
import useUser from '../hooks/useUser';

const Shelter = () => {
    const { user, setUser } = useUser({ userType: USERS.SHELTER })

    return (
        <>
            <Header />
            <main>
                <AdoptionSection />
            </main>
            <Footer />
        </>

    );
}

export default Shelter;