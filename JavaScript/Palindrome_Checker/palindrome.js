function palindrome(str) {
    var badChars = /[\W!,.'"_]/g; 

    var forwardString = str.toLowerCase().replace(badChars, '');

    var backwardString = forwardString.split('').reverse().join(''); 

    return forwardString === backwardString; 
}
palindrome("eye");