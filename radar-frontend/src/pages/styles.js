import  styled  from "styled-components";

export const Main = styled.div`
    flex : 1;
    justify-content: center;
    align-items: center;
    display: flex;
    width: 100%;
    height: 100%
    flex-direction: column;
    margin-top:20px;
`

export const Container = styled.div`
    display:flex;
    flex-direction: row;

    > div {
        width : 50%
    }

    h1 {
        font-size : 56px;
        font-weight: bold;
    }

    h6 {
        font-size: 16px;
        font-weight: normal;
        padding-right: 150px;
        margin-top: 25px;
    }
`